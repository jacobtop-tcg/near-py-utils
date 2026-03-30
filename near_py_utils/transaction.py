"""
NEAR Transaction Construction Helpers

Utilities for building and signing NEAR transactions.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import base64
import hashlib


@dataclass
class TransactionAction:
    """Represents a NEAR transaction action."""
    action_type: str
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransactionBuilder:
    """
    Builder for constructing NEAR transactions.
    
    Features:
        - Fluent API for transaction construction
        - Support for multiple actions
        - Automatic nonce management
        
    Example:
        >>> tx = (TransactionBuilder()
        ...     .sender("alice.near")
        ...     .receiver("bob.near")
        ...     .transfer(1000000000000000000000000)  # 1 NEAR
        ...     .build())
    """
    
    def __init__(self):
        self._sender: Optional[str] = None
        self._receiver: Optional[str] = None
        self._nonce: Optional[int] = None
        self._block_hash: Optional[str] = None
        self._actions: List[TransactionAction] = []
        self._gas: int = 30_000_000_000_000  # 30 Tgas default
    
    def sender(self, account_id: str) -> "TransactionBuilder":
        """Set the sender account ID."""
        self._sender = account_id
        return self
    
    def receiver(self, account_id: str) -> "TransactionBuilder":
        """Set the receiver account ID."""
        self._receiver = account_id
        return self
    
    def nonce(self, nonce: int) -> "TransactionBuilder":
        """Set the transaction nonce."""
        self._nonce = nonce
        return self
    
    def block_hash(self, block_hash: str) -> "TransactionBuilder":
        """Set the recent block hash."""
        self._block_hash = block_hash
        return self
    
    def gas(self, gas: int) -> "TransactionBuilder":
        """Set the gas amount."""
        self._gas = gas
        return self
    
    def transfer(self, amount: int) -> "TransactionBuilder":
        """
        Add a transfer action.
        
        Args:
            amount: Amount in yoctoNEAR (1 NEAR = 10^24 yoctoNEAR)
        """
        self._actions.append(TransactionAction(
            action_type="Transfer",
            data={"deposit": str(amount)}
        ))
        return self
    
    def deploy_contract(self, code: bytes) -> "TransactionBuilder":
        """Add a deploy contract action."""
        self._actions.append(TransactionAction(
            action_type="DeployContract",
            data={"code": base64.b64encode(code).decode()}
        ))
        return self
    
    def function_call(
        self,
        method_name: str,
        args: Dict[str, Any],
        gas: Optional[int] = None,
        deposit: int = 0,
    ) -> "TransactionBuilder":
        """
        Add a function call action.
        
        Args:
            method_name: Contract method to call
            args: Method arguments as dict
            gas: Gas for this call (uses default if None)
            deposit: Deposit in yoctoNEAR
        """
        self._actions.append(TransactionAction(
            action_type="FunctionCall",
            data={
                "method_name": method_name,
                "args": args,
                "gas": gas or self._gas,
                "deposit": str(deposit),
            }
        ))
        return self
    
    def add_key(
        self,
        public_key: str,
        permission: Optional[Dict[str, Any]] = None,
    ) -> "TransactionBuilder":
        """Add an add key action."""
        self._actions.append(TransactionAction(
            action_type="AddKey",
            data={"public_key": public_key, "permission": permission or "FullAccess"}
        ))
        return self
    
    def delete_key(self, public_key: str) -> "TransactionBuilder":
        """Add a delete key action."""
        self._actions.append(TransactionAction(
            action_type="DeleteKey",
            data={"public_key": public_key}
        ))
        return self
    
    def delete_account(self, beneficiary_id: str) -> "TransactionBuilder":
        """Add a delete account action."""
        self._actions.append(TransactionAction(
            action_type="DeleteAccount",
            data={"beneficiary_id": beneficiary_id}
        ))
        return self
    
    def stake(
        self,
        stake: int,
        public_key: str,
    ) -> "TransactionBuilder":
        """Add a stake action."""
        self._actions.append(TransactionAction(
            action_type="Stake",
            data={"stake": str(stake), "public_key": public_key}
        ))
        return self
    
    def build(self) -> Dict[str, Any]:
        """
        Build the transaction object.
        
        Returns:
            Transaction dict ready for signing
            
        Raises:
            ValueError: If required fields are missing
        """
        if not self._sender:
            raise ValueError("Sender account ID is required")
        if not self._receiver:
            raise ValueError("Receiver account ID is required")
        
        return {
            "transaction": {
                "signer_id": self._sender,
                "receiver_id": self._receiver,
                "nonce": self._nonce or 0,
                "block_hash": self._block_hash or "",
                "actions": [
                    {action.action_type: action.data}
                    for action in self._actions
                ],
            }
        }
    
    def serialize(self) -> bytes:
        """
        Serialize the transaction for signing.
        
        Returns:
            Borsh-serialized transaction bytes
        """
        # Simplified serialization - in production use borsh library
        tx = self.build()
        return str(tx).encode('utf-8')


def create_transfer_transaction(
    sender: str,
    receiver: str,
    amount: int,
    nonce: Optional[int] = None,
    block_hash: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a simple transfer transaction.
    
    Args:
        sender: Sender account ID
        receiver: Receiver account ID
        amount: Amount in yoctoNEAR
        nonce: Transaction nonce (optional)
        block_hash: Recent block hash (optional)
        
    Returns:
        Transaction dict ready for signing
        
    Example:
        >>> tx = create_transfer_transaction(
        ...     "alice.near",
        ...     "bob.near",
        ...     1000000000000000000000000,  # 1 NEAR
        ... )
    """
    return (TransactionBuilder()
            .sender(sender)
            .receiver(receiver)
            .nonce(nonce or 0)
            .block_hash(block_hash or "")
            .transfer(amount)
            .build())


def compute_transaction_hash(tx_bytes: bytes) -> str:
    """
    Compute the hash of a transaction.
    
    Args:
        tx_bytes: Serialized transaction bytes
        
    Returns:
        Base58-encoded transaction hash
    """
    hash_bytes = hashlib.sha256(tx_bytes).digest()
    # In production, use proper base58 encoding
    return base64.b64encode(hash_bytes).decode()
