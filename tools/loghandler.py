import os
import logging
import time

logger_name = "lendliquidate_Logger"


def cal_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        spend = end - start
        name = func.__name__
        print("\n{} spend : {}\n".format(name, spend))

    return wrapper


def create_logger(logname):
    """返回日志对象"""
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # 创建日志文件
    fh = logging.FileHandler(
        # 例如：../log/settlement.log
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/log/{}.log".format(logname)
    )

    # 设置日志格式
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    return logger

