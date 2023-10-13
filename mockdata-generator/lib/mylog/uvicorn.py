import os
import sys
import logging
from . import logger, format_record, InterceptHandler, LOG_PATH

# 標準的 logger file 路徑
ACCESS_LOG = os.path.join(LOG_PATH, "access.log")
ERROR_LOG = os.path.join(LOG_PATH, "error.log")

def init_uvicorn():
    """
    init_uvicorn 提供一個初始化 uvicorn logger 的簡易方法，
    主要是為了讓 uvicorn 的 logger 也能夠使用 loguru 的 logger。
    """
    intercept_handler = InterceptHandler()
    loggers = (
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name.startswith("uvicorn.")
    )
    # 清空 uvicorn 的 logger，避免重複輸出
    for uvicorn_logger in loggers:
        uvicorn_logger.handlers = []

    # 把 uvicorn 的 logger 設定成 loguru 的 logger
    # 注意: uvicorn 的 logger 會輸出到 sys.stdout，所以要設定成 loguru 的 logger
    logging.getLogger("uvicorn.access").handlers = [intercept_handler]
    logging.getLogger("uvicorn").handlers = [intercept_handler]
    
    # 新增檔案輸出的 logger
    logger.add(ACCESS_LOG, enqueue=True, rotation="20 MB", level="INFO")
    logger.add(ERROR_LOG, enqueue=True, rotation="10 MB", level="ERROR")

    # 配置loguru的日志句柄，sink代表输出的目标
    logger.configure(
        handlers=[
            {"sink": sys.stdout, "level": logging.DEBUG, "format": format_record},
            {"sink": ACCESS_LOG, "level": logging.INFO},
            {"sink": ERROR_LOG, "level": logging.ERROR}
        ]
    )