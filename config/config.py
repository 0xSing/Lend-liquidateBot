import os

# Polygon Node Rpc
POLYGON_RPC_URL = os.environ.get('POLYGON_RPC_URL', 'https://polygon-rpc.com')

# timeout for get transaction receipt(sec)
TX_TIMEOUT = os.environ.get('TX_TIMEOUT', 300)

# profit account key
PROFIT_KEY = os.environ.get('PROFIT_KEY','./key_file')

# Gas Price
GAS_PRICE = int(os.environ.get('GAS_PRICE', 1000000))

# Transaction Failure Topics0
FAILURE_TOPICS0 = os.environ.get('FAILURE_TOPICS0', '0x45b96fe442630264581b197e84bbada861235052c5a1aadfff9ea4e40a969aa0')

# work interval time
WORK_INTERVAL = os.environ.get('WORK_INTERVAL', 43200)

# contract address
MAX_NUM = int(os.environ.get('MAX_NUM', 100))
# sequence (CGF -> NUSD -> DG -> MATIC -> WMATIC -> USDC)
IS_USE_WHITELIST = os.environ.get('IS_USE_WHITELIST', False)
POOLS_LIST = os.environ.get('POOLS_LIST', '["0x99E861b44140446C233a741426d6aD3f46a4ccEf","0xc9426c6AE38eAdCa76905c2e0DbEc0803F031D11"]')
POOL_BLACK_LIST = os.environ.get('POOL_BLACK_LIST','[]')

# DPLend system api
POOLS_API_URL = os.environ.get('POOLS_API_URL','https://test.dpcprotocol.com/lendApi/pools/getTokenAddressList')
LIQUIDATE_LIST_URL = os.environ.get('LIQUIDATE_LIST_URL','https://test.dpcprotocol.com/lendApi/market/liquidationInPool')
