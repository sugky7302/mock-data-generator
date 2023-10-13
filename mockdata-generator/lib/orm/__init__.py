# -*- encoding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from .model import ORM, ORMInfo
from .oracle import Oracle
import lib.mylog.orm as ormlog

ormlog.init_orm()
BASE = declarative_base()

INSTANCES = {}
DRIVERS: dict[str, ORM] = {
    "oracle": Oracle
}

def make_orm(conn: ORMInfo) -> ORM:
    """
    根據 driver 生成對應的 ORM 物件
    """
    key = conn.signature
    if key not in INSTANCES:
        orm = DRIVERS[conn.driver](conn)
        INSTANCES[key] = orm

    return INSTANCES[key]