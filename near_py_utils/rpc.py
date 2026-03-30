"""
NEAR RPC Client with Retry Logic

Async and sync RPC client for NEAR Protocol with automatic retry support.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
import aiohttp


@dataclass
class NearRpcError(Exception):
    """RPC error from NEAR node."""
    code: int
    message: str
    data: Optional[str] = None


class NearRpcClient:
    """
    Async RPC client for NEAR Protocol with retry logic.
    
    Features:
        - Automatic retry with exponential backoff
        - Configurable timeout
        - Support for multiple RPC endpoints
        - Type-safe responses
        
    Args:
        rpc_url: NEAR RPC endpoint URL
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        timeout: Request timeout in seconds
        
    Example:
        >>> async with NearRpcClient() as client:
        ...     account = await client.get_account("example.near")
        ...     print(account)
    """
    
    DEFAULT_RPC_URL = "https://rpc.mainnet.near.org"
    TESTNET_RPC_URL = "https://rpc.testnet.near.org"
    
    def __init__(
        self,
        rpc_url: Optional[str] = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        timeout: float = 30.0,
    ):
        self.rpc_url = rpc_url or self.DEFAULT_RPC_URL
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self) -> "NearRpcClient":
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._session:
            await self._session.close()
    
    async def _request(
        self,
        method: str,
        params: List[Any],
        retry_count: int = 0,
    ) -> Dict[str, Any]:
        """Make an RPC request with retry logic."""
        payload = {
            "jsonrpc": "2.0",
            "id": f"near-py-utils-{int(time.time() * 1000)}",
            "method": method,
            "params": params,
        }
        
        try:
            if not self._session:
                raise RuntimeError("Client not initialized. Use 'async with' context manager.")
            
            async with self._session.post(
                self.rpc_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            ) as response:
                result = await response.json()
                
                if "error" in result:
                    error = result["error"]
                    raise NearRpcError(
                        code=error.get("code", -1),
                        message=error.get("message", "Unknown error"),
                        data=error.get("data"),
                    )
                
                return result.get("result", {})
                
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if retry_count < self.max_retries:
                delay = self.base_delay * (2 ** retry_count)
                await asyncio.sleep(delay)
                return await self._request(method, params, retry_count + 1)
            raise NearRpcError(code=-1, message=f"Request failed after {self.max_retries} retries: {str(e)}")
    
    async def get_account(self, account_id: str) -> Dict[str, Any]:
        """
        Get account information.
        
        Args:
            account_id: The account ID to query
            
        Returns:
            Account information including amount, locked, code_hash, etc.
        """
        return await self._request("query", [
            {"request_type": "view_account", "finality": "final", "account_id": account_id}
        ])
    
    async def get_block(self, block_id: Optional[Union[str, int]] = None) -> Dict[str, Any]:
        """
        Get block information.
        
        Args:
            block_id: Block height or hash. If None, returns latest block.
            
        Returns:
            Block information
        """
        if block_id is None:
            return await self._request("block", [None])
        return await self._request("block", [block_id])
    
    async def get_status(self) -> Dict[str, Any]:
        """Get node status."""
        return await self._request("status", [None])
    
    async def send_transaction(self, signed_transaction: str) -> Dict[str, Any]:
        """
        Send a signed transaction.
        
        Args:
            signed_transaction: Base64-encoded signed transaction
            
        Returns:
            Transaction result
        """
        return await self._request("broadcast_tx_async", [signed_transaction])
    
    async def view_call(
        self,
        account_id: str,
        method_name: str,
        args_base64: str = "",
    ) -> Dict[str, Any]:
        """
        Call a view method on a contract.
        
        Args:
            account_id: Contract account ID
            method_name: Method to call
            args_base64: Base64-encoded arguments
            
        Returns:
            Call result
        """
        return await self._request("query", [
            {
                "request_type": "call_function",
                "finality": "final",
                "account_id": account_id,
                "method_name": method_name,
                "args_base64": args_base64,
            }
        ])


# Sync wrapper for convenience
class SyncNearRpcClient:
    """Synchronous wrapper around NearRpcClient."""
    
    def __init__(self, **kwargs):
        self._client = NearRpcClient(**kwargs)
        self._loop = None
    
    def _get_loop(self):
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
        return self._loop
    
    def get_account(self, account_id: str) -> Dict[str, Any]:
        """Get account information (sync)."""
        loop = self._get_loop()
        
        async def call():
            async with self._client as client:
                return await client.get_account(account_id)
        
        return loop.run_until_complete(call())
    
    def close(self):
        """Cleanup."""
        if self._loop and not self._loop.is_closed():
            self._loop.close()
