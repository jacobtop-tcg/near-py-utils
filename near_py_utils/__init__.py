"""
NEAR Protocol Python Utilities

A collection of utilities for NEAR Protocol development including:
- Account ID validation
- Transaction construction helpers
- RPC client with retry logic
"""

from .account import validate_account_id, is_valid_account_id, AccountValidationError
from .transaction import TransactionBuilder, create_transfer_transaction
from .rpc import NearRpcClient, NearRpcError
from .types import AccountID, NearAmount, BlockHeight

__version__ = "1.0.0"
__all__ = [
    "validate_account_id",
    "is_valid_account_id",
    "AccountValidationError",
    "TransactionBuilder",
    "create_transfer_transaction",
    "NearRpcClient",
    "NearRpcError",
    "AccountID",
    "NearAmount",
    "BlockHeight",
]
