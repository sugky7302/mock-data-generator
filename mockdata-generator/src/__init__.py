# -*- encoding: utf-8 -*-
'''
整個程式的進入點
'''
from datetime import datetime, timedelta
import random
from lib.orm import make_orm
from lib.orm.model import ORMInfo
from config import settings
from src.models.fab_pressure import FabPressure
from lib.mylog import logger

orm_info = ORMInfo(
    driver=settings.database.driver,
    host=settings.database.host,
    port=settings.database.port,
    database=settings.database.database,
    account=settings.database.account,
    password=settings.database.password
)

def generate_mockdata():
    '''
    generate_mockdata 是生成 Oracle 假數據到資料庫的方法。
    '''

    # 假資料的總筆數
    TOTAL = 10000
    # 每批次新增的資料筆數，新增後會 commit
    BATCH_SIZE = 2000
    # 廠區
    FABS = ["FAB8AB", "FAB8C", "FAB8D", "FAB8E", "FAB8F", "FAB8S"]
    # 當前時間，用來隨機 UPDATE_TIME
    now = datetime.now()
    interval = 86400 * 7
    # 氣壓標準
    STANDARD_PRESSURE = 1000

    logger.info(f"開始新增 {TOTAL} 筆假資料到資料庫 {orm_info.signature}/{orm_info.driver}...")
    logger.info(f"每次新增 {BATCH_SIZE} 筆資料...")
    logger.info(f"進度: 0/{TOTAL}(0%)", end="")
    with make_orm(orm_info) as db:
        for i in range(TOTAL):
            db.add(FabPressure(
                fab=FABS[i % len(FABS)],
                time=(now + timedelta(seconds=random.randint(-interval,0))),
                pressure=STANDARD_PRESSURE + 70*random.random() - 35,
                eqp=f'eqp-{random.randint(0, 9)}'
            ))

            # 每個 batch_size 或最後一筆資料時 commit
            if (i % BATCH_SIZE == BATCH_SIZE - 1) or (i == TOTAL - 1):
                logger.info(f"進度: {i+1}/{TOTAL}({(i+1)/TOTAL:.1%})", end="")
                try:
                    db.commit()
                finally:
                    pass


if __name__ == "__main__":
    generate_mockdata()