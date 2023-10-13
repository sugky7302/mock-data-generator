# -*- coding: utf-8 -*-
"""
建立一個規範好的 logger 模組，讓未來的 Python 專案可以直接使用。
參考:
- https://gist.github.com/shambarick/51c955e55cf61a9e6e339f4c0223b938
- https://segmentfault.com/q/1010000042109567
- https://github.com/ycc140/fastapi_mongo/blob/main/part4/src/custom_logging.py
"""
import os
import logging
from pprint import pformat
from loguru import logger

LOG_FORMAT = '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>'

# Create log folder if not exists
LOG_PATH = os.path.join(os.getcwd(), "logs")
if not os.path.isdir(LOG_PATH):
    os.mkdir(LOG_PATH)

class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentaion.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def format_record(record: dict) -> str:
    """
    自訂 logger 格式，並且將 payload 轉換成可讀性高的格式。
    要設定在 logger.add() 的 format 參數中。

    Example:
    # >>> payload = [{"users":[{"name": "Nick", "age": 87, "is_active": True}, {"name": "Alex", "age": 27, "is_active": True}], "count": 2}]
    # >>> logger.bind(payload=).debug("users payload")
    # >>> [   {   'count': 2,
    # >>>         'users': [   {'age': 87, 'is_active': True, 'name': 'Nick'},
    # >>>                      {'age': 27, 'is_active': True, 'name': 'Alex'}]}]
    """

    format_string = LOG_FORMAT
    
    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"

    format_string += "{exception}\n"

    return format_string
