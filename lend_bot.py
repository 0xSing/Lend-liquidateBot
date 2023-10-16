from tools.util import logger
from tools import loghandler,util
from keeper import Keeper
import signal

_log = loghandler.create_logger('main')

def log_it(content):
    logger.info(content)
    _log.exception(content)

if __name__ == '__main__':
    Keeper().main()
    # Watcher().run()