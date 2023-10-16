import time
import json
import requests
import logging
import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('-')


def read_json(path):
    with open(path, 'r') as load_f:
        data = json.load(load_f)
    return data


def trans_time(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)


def today_date():
    return datetime.datetime.now().strftime('%Y-%m-%d')


def today_timestamp():
    today = datetime.date.today()
    return int(time.mktime(today.timetuple()))


def trans_timestamp(dt):
    # 时间数组
    timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
    # 时间戳
    return time.mktime(timeArray)


def now_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def data_is_useful(*args):
    return all(args)


def get_period(now_minute):
    cuts = (range(55, -5, -5))
    for start_time in cuts:
        if now_minute >= start_time:
            return start_time


def time_to_update(start_hour: int, end_hour: int):
    """是否在指定的时间范围内"""
    now_hour = datetime.datetime.now().hour
    return start_hour <= now_hour <= end_hour


def get_timestamp_spec_time(hour, minute=0, days=0):
    """
    获取指定的时间点的时间戳
    :param clock: 钟点;指定的时间,比如当天的凌晨一点,钟点即为1(24小时制)
    :param days:  与当前时间的相差的日期。-1 表示昨天；0 表示当天(默认)；1 表示明天
    :return:      返回时间戳
    """
    now_time = datetime.datetime.now() + datetime.timedelta(days=days)
    specified_time = now_time.strftime("%Y-%m-%d") + " {}:{}:00".format(hour, minute)
    time_tuple = time.strptime(specified_time, "%Y-%m-%d %H:%M:%S")
    return time.mktime(time_tuple)


def send_msg(content, url):
    params = {"msgtype": "text", "text": {"content": content}}
    params = json.dumps(params).encode(encoding='utf-8')
    headers = {"Content-Type": "application/json; charset=utf-8"}
    res = requests.post(url, data=params, headers=headers, timeout=3)
    result = json.loads(res.content.decode('utf-8'))
    print('[DingDing send mail result] --> ', result)


def http_get(url, params=None):
    res = requests.get(url, params=params, timeout=5, verify=False)
    decode_result = res.content.decode('utf-8')
    result = json.loads(decode_result)
    return result


def http_post(url, params):
    res = requests.post(url, data=params, verify=False)
    decode_result = res.content.decode('utf-8')
    result = json.loads(decode_result)
    return result


def http_put(url, params):
    res = requests.put(url, data=params, verify=False)
    decode_result = res.content.decode('utf-8')
    result = json.loads(decode_result)
    return result
