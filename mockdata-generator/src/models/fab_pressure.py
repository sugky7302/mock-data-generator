"""
這個腳本是放置資料表映射到程式的 DAO 物件
因為 SQLAlchemy 一定要有主鍵，所以記得要指定 Column 為主鍵，
不然會出現錯誤訊息:
「sqlalchemy.exc.ArgumentError: Mapper Mapper[ClassName(TableName)]
could not assemble any primary key columns for mapped table 'TableName'
"""
from lib.orm import BASE
from sqlalchemy import Column, String, Float, Date

class FabPressure(BASE):
    __tablename__ = 'VW_SPC_CHARTDATA_CHAM_PRESS'

    fab=Column("FAB", String(20))
    time=Column("UPDATE_TIME", Date, primary_key=True)
    eqp=Column("PROCESSUNIT", String(20))
    pressure=Column("MEAN_VALUE", Float)
