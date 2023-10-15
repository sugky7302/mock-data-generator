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

def generate_mockdata(total: int,batch: int = 2000, interval: int = 86400*7):
    '''
    generate_mockdata 是生成 Oracle 假數據到資料庫的方法。

    Args:
        total (int): 假資料的總筆數。
        batch (int): 每批次新增的資料筆數，新增後會 commit。預設是 2000 筆提交一次。
        interval (int): 資料分佈間隔，單位為秒，預設為 86400*7 (一週)。
    '''

    # 廠區
    FABS = ["FAB8AB", "FAB8C", "FAB8D", "FAB8E", "FAB8F", "FAB8S"]
    # 當前時間，用來隨機 UPDATE_TIME
    now = datetime.now()
    # 氣壓標準
    STANDARD_PRESSURE = 1000

    logger.info(f"開始新增 {total} 筆假資料到資料庫 {orm_info.signature}/{orm_info.driver}...")
    logger.info(f"每次新增 {batch} 筆資料...")
    logger.info(f"進度: 0/{total}(0%)", end="")
    with make_orm(orm_info) as db:
        for i in range(total):
            db.add(FabPressure(
                fab=FABS[i % len(FABS)],
                time=(now + timedelta(seconds=random.randint(-interval,0))),
                pressure=STANDARD_PRESSURE + 70*random.random() - 35,
                eqp=f'eqp-{random.randint(0, 9)}'
            ))

            # 每個 batch_size 或最後一筆資料時 commit
            if (i % batch == batch - 1) or (i == total - 1):
                logger.info(f"進度: {i+1}/{total}({(i+1)/total:.1%})", end="")
                try:
                    db.commit()
                finally:
                    pass
    logger.info("新增完成，一共花費了 %s 秒", (datetime.now() - now).total_seconds())


if __name__ == "__main__":
    #? 做成可以接收命令列參數的程式，可以查詢 argparse 套件
    generate_mockdata()