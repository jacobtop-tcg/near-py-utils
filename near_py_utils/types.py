"""
Type definitions for NEAR Python Utilities.
"""

from typing import NewType, Union

# Account ID type (e.g., "example.near", "test.testnet")
AccountID = NewType('AccountID', str)

# Amount in yoctoNEAR (1 NEAR = 10^24 yoctoNEAR)
NearAmount = NewType('NearAmount', int)

# Block height
BlockHeight = NewType('BlockHeight', int)

# Gas amount
GasAmount = NewType('GasAmount', int)

# Shard ID
ShardId = NewType('ShardId', int)

# Epoch ID
EpochId = NewType('EpochId', str)

# Crypto hash (base58 encoded)
CryptoHash = NewType('CryptoHash', str)

# Signature (base58 encoded)
Signature = NewType('Signature', str)

# Public key (base58 encoded)
PublicKey = NewType('PublicKey', str)

# Common type aliases
AccountIdOrString = Union[AccountID, str]
AmountOrInt = Union[NearAmount, int]

# NEAR denomination constants
YOCTO_PER_NEAR = 10**24
YOCTO_PER_MILLI_NEAR = 10**21
YOCTO_PER_MICRO_NEAR = 10**18

def near_to_yocto(near: float) -> NearAmount:
    """Convert NEAR to yoctoNEAR."""
    return NearAmount(int(near * YOCTO_PER_NEAR))

def yocto_to_near(yocto: int) -> float:
    """Convert yoctoNEAR to NEAR."""
    return yocto / YOCTO_PER_NEAR
