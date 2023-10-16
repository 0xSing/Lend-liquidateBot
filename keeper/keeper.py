import json
import threading
import config
import requests
from watcher import Watcher
from tools import loghandler
from tools.address import Address
from tools.util import logger
from web3 import Web3, HTTPProvider
from web3.middleware import construct_sign_and_send_raw_middleware, geth_poa_middleware
from eth_account import Account
from contract.token_pool import TokenPool
from contract.ether_pool import EtherPool

_log = loghandler.create_logger('keeper')


def log_it(content):
    logger.info(content)
    _log.exception(content)

class Keeper:

    def __init__(self):
        self.profit_account = None
        # init web3 node
        self.web3 = Web3(HTTPProvider(endpoint_uri=config.POLYGON_RPC_URL, request_kwargs={'timeout': 60}))
        self.web3.middleware_onion.inject(geth_poa_middleware,layer=0)

        # init gas_price
        self.gas_price = self.web3.eth.gasPrice + config.GAS_PRICE

        # init perpetuals list
        self.perpetutals = {}

        # init watcher
        self.watcher = Watcher(self.web3)

        # init nonce
        self.nonce = 0

        # init thread lock
        self.lock = threading.Lock()

        # TODO reader init

    def _check_profit_account(self):
        with open(config.PROFIT_KEY) as f:
            profit_key = f.read().replace("\n","").replace(" ","")
            try:
                account = Account()
                acc = account.from_key(profit_key)
                print(acc.address)
                self.profit_account = Address(acc.address)

                # set send middleware
                self.web3.middleware_onion.add(construct_sign_and_send_raw_middleware(acc))

                # set account nonce
                self.nonce = self.web3.eth.getTransactionCount(self.profit_account.address)

            except Exception as e:
                _log.exception(f"check private key error: {e}")
                return False
        return True

    def _set_ptoken_pools(self):
        if config.IS_USE_WHITELIST:
            pool_addrs = json.loads(config.POOLS_LIST)
            for pool_addr in pool_addrs:
                if str(pool_addr) == '0x0ec73547B4905Feb54a63a483B42f2f3C71d448f':
                    pool = EtherPool(web3=self.web3, address=Address(pool_addr))
                else:
                    pool = TokenPool(web3=self.web3, address=Address(pool_addr))

                self.perpetutals[pool_addr] = pool
        else:
            self._get_remote_pools()


    def _get_remote_pools(self):
        try:
            res = requests.get(config.POOLS_API_URL, timeout=20)
            if res.status_code == 200:
                resJson = res.json()
                pool_addrs = resJson['data']
                for pool_addr in pool_addrs:
                    if pool_addr in config.POOL_BLACK_LIST.lower():
                        _log.warning(f"pool in black list: {pool_addr}")
                        continue

                    if str(pool_addr) == '0x0ec73547B4905Feb54a63a483B42f2f3C71d448f':
                        pool = EtherPool(web3=self.web3, address=Address(pool_addr))
                    else:
                        pool = TokenPool(web3=self.web3, address=Address(pool_addr))

                    self.perpetutals[pool_addr] = pool
        except Exception as e:
            _log.exception(f"get all perpetuals from api error: {e}")

    def _check_all_pools(self):
        def thread_fun(pool):
            self._check_all_accounts(pool)

        # must set ptoken pool first
        if len(self.perpetutals) == 0:
            self._set_ptoken_pools()

        # init thread_list
        thread_list = []
        for pool in self.perpetutals.keys():
            thread = threading.Thread(target=thread_fun, args=(pool,))
            thread_list.append(thread)

        for i in range(len(thread_list)):
            thread_list[i].start()

        for i in range(len(thread_list)):
            thread_list[i].join()

        _log.info(f"check all pools end!")

    def _check_all_accounts(self, pool):
        pool = self.perpetutals[pool]
        print(f"{pool.tokenPoolName()}-thread working")
        is_continue = True

        # check all need liquidated account in this pool
        while is_continue:
            params = {
                'pTokenAddr': pool.address
            }
            res = requests.get(config.LIQUIDATE_LIST_URL, params=params, timeout=20)
            if res.status_code == 200:
                if len(res.json()) < config.MAX_NUM:
                    is_continue = False
                accounts = res.json()
            else:
                _log.exception(f"getAccountInfo error:{res.content}")

            for account in accounts:
                _log.info(f"check_account pool_address:{pool.address} address:{account.get('borrower')} ptokenCollaterals:{account.get('ptokenCollaterals')} borrowAmount:{account.get('borrowAmount')}")
                # TODO check account at lendAsset contract
                try:
                    for strategy in account.get('strategy'):
                        borrower = Web3.toChecksumAddress(account.get('borrower'))
                        repayAmount = int(strategy.get('repayAmount'))
                        collateral = Web3.toChecksumAddress(strategy.get('collateral'))
                        self.gas_price = self.web3.eth.gasPrice + config.GAS_PRICE
                        print(borrower)
                        print(repayAmount)
                        print(collateral)
                        print(self.gas_price)
                        print(self.nonce)

                        self.lock.acquire()
                        tx_hash = pool.liquidateBorrow(borrower=borrower,
                                                       repayAmount=repayAmount,
                                                       pTokenCollateral=collateral,
                                                       profit=self.profit_account,
                                                       gas_price=self.gas_price,
                                                       nonce=self.nonce)

                        self.nonce = self.nonce + 1
                        self.lock.release()

                        transaction_status = self._wait_transaction_receipt(tx_hash, 10)
                        if transaction_status:
                            _log.info(f"liquidate success. address:{account.get('borrower')}")
                        else:
                            _log.info(f"liquidate fail. address:{account.get('borrower')}")

                except Exception as e:
                    _log.exception(f"liquidate failed. address:{account.get('borrower')} error:{e}")



    def _wait_transaction_receipt(self, tx_hash, times):
        _log.info(f"tx_hash:{self.web3.toHex(tx_hash)}")
        for i in range(times):
            try:
                tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash, config.TX_TIMEOUT)
                _log.info(tx_receipt)
                status = tx_receipt['status']
                logs = tx_receipt['logs']

                if status == 0:
                    return False
                elif status == 1:
                    for log in logs:
                        if log.topics[0].hex() == config.FAILURE_TOPICS0:
                            return False
                    return True
            except:
                continue


    def main(self):
        if self._check_profit_account():
            self._set_ptoken_pools()
            self._check_all_pools()
            # self.watcher.add_block_syncer(self._check_all_pools)
            # self.watcher.run()






