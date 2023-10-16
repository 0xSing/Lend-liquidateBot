from web3 import Web3

from tools.contract import Contract
from tools.address import Address

class TokenPool(Contract):
    abi = Contract._load_abi(__name__, '../abis/Perc20.abi')

    def __init__(self, web3: Web3, address: Address):
        assert(isinstance(web3, Web3))
        assert(isinstance(address, Address))

        self.web3 = web3
        self.address = address
        self.contract = self._get_contract(web3, self.abi, address)

    def tokenPoolName(self):
        return self.contract.functions.symbol().call()

    def liquidateBorrow(self, borrower, repayAmount, pTokenCollateral, profit, gas_price, nonce):
        tx_hash = self.contract.functions.liquidateBorrow(borrower, repayAmount, pTokenCollateral).transact({
                    'from': profit.address,
                    'gasPrice': gas_price,
                    'gas': 1000000,
                    'nonce': nonce,
                })
        return tx_hash
