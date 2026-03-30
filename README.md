# NEAR Python Utilities

Python utilities for NEAR Protocol development.

## Features

- Account ID validation
- Transaction construction helpers
- RPC client with retry logic
- Full type hints
- Async support

## Installation

```bash
pip install near-py-utils
```

## Usage

```python
from near_py_utils import validate_account_id, NearRpcClient

# Validate account ID
valid = validate_account_id("example.near")

# Use async RPC client
async with NearRpcClient() as client:
    account = await client.get_account("example.near")
```

## License

MIT
