import threading
import time
import config
from web3 import Web3
from tools.util import logger
from tools import loghandler
import signal

_log = loghandler.create_logger('watcher')

class Watcher:

    def __init__(self, web3: Web3 = None):
        self.web3 = web3
        self.block_syncers = []

        self.terminated = False
        self._last_block_time = None

    def add_block_syncer(self, callback):
        assert(callable(callback))
        assert(self.web3 is not None)
        self.block_syncers.append(AsyncThread(callback))

    def run(self):
        if self.web3 is None:
            _log.exception("Init Web3 and set for watcher")
            return
        _log.info(f"Keeper connected to {self.web3.provider}")

        self._start_watching_blocks()
        _log.info("Keeper shut down")

    def _start_watching_blocks(self):
        # TODO linux signal listener
        signal.signal(signal.SIGINT, self._sigal_handler)
        signal.signal(signal.SIGTERM, self._sigal_handler)

        _log.info("Watching for new blocks")

        # while True:
        #     if self.terminated:
        #         break

        self._sync_block()
        time.sleep(config.WORK_INTERVAL)

        for block_syncer in self.block_syncers:
            block_syncer.wait()


    def _sync_block(self):
        self._last_block_time = int(time.time())

        if self.terminated:
            _log.debug(f"Ignoring block as keeper is already terminating")

        def on_start():
            _log.debug(f"Processing the syncer")

        def on_finish():
            _log.debug(f"Finished processing the syncer")

        for block_syncer in self.block_syncers:
            if not block_syncer.run(on_start, on_finish):
                _log.debug(f"Ignoring as previous callback is still running")

    def _sigal_handler(self, sig, frame):
        # Listening the linux signal
        print("Got the linux signal")
        if self.terminated:
            _log.warning("Keeper termination already in progress")
        else:
            _log.warning("Keeper received SIGINT/SIGTERM signal, will terminate gracefully")
            self.terminated = True


class AsyncThread:

    def __init__(self, callback):
        self.callback = callback
        self.thread = None

    def run(self, on_start=None, on_finish=None) -> bool:
        # make sure the same block_syncer only one thread at the same time
        if self.thread is None or not self.thread.is_alive():
            def thread_target():
                if on_start is not None:
                    on_start()
                self.callback()
                if on_finish is not None:
                    on_finish()

            self.thread = threading.Thread(target=thread_target)
            self.thread.start()
            return True
        else:
            _log.info("thread fail")
            return False

    def wait(self):
        if self.thread is not None:
            self.thread.join()
















