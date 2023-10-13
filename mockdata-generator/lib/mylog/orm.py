import os
import sys
import logging
from . import logger, format_record, InterceptHandler, LOG_PATH

# 標準的 logger file 路徑
SQL_LOG = os.path.join(LOG_PATH, "sql.log")

def init_orm():
    """
    init_orm 提供一個初始化 orm logger 的簡易方法，
    主要是為了讓 orm 的 logger 也能夠使用 loguru 的 logger。
    """
    intercept_handler = InterceptHandler()
    loggers = (
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name.startswith("orm.")
    )
    # 清空 orm 的 logger，避免重複輸出
    for orm_logger in loggers:
        orm_logger.handlers = []

    # 把 orm 的 logger 設定成 loguru 的 logger
    # 注意: orm 的 logger 會輸出到 sys.stdout，所以要設定成 loguru 的 logger
    logging.getLogger("orm").handlers = [intercept_handler]
    
    # 新增檔案輸出的 logger
    logger.add(SQL_LOG, enqueue=True, rotation="20 MB", level="INFO")

    # 配置loguru的日志句柄，sink代表输出的目标
    logger.configure(
        handlers=[
            {"sink": sys.stdout, "level": logging.DEBUG, "format": format_record},
            {"sink": SQL_LOG, "level": logging.INFO},
        ]
    )