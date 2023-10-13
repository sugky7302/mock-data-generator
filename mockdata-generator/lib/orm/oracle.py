from .model import ORM
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

class Oracle(ORM):
    '''
    Oracle 使用 oracledb 這個驅動程式來連線資料庫，
    讓 SQLAlchemy 可以透過 oracledb 來連線資料庫。
    '''
    # 預設 oracledb 不會使用 Oracle Instant Client
    thick_mode = None

    @property
    def dsn(self) -> str:
        '''
        雖然抽象屬性已經有定義 @property 了，
        但是實現 dsn 的時候，記得上面要補 @property，不然會報錯。
        這裡會自動判斷使用哪個模組，然後產生對應的 dsn。
        '''
        try:
            import oracledb
            return f"oracle+oracledb://{self.conn.account}:{self.conn.password}@{self.conn.host}:{self.conn.port}/?service_name={self.conn.database}" 
        except ImportError:
            pass

        try:
            import cx_Oracle
            return f"oracle+cx_oracle://{self.conn.account}:{self.conn.password}@{self.conn.host}:{self.conn.port}/?service_name={self.conn.database}" 
        except ImportError:
            pass
        
        raise Exception("未偵測到 oracledb 或 cx_Oracle 模組，這會導致無法連線 Oracle 資料庫。推薦安裝 oracledb 1.4.2+ 或者 cx_Oracle 8.3.0+。")
    
    def connect(self) -> Session:
        self.engine = create_engine(self.dsn, thick_mode=self.thick_mode)
        return sessionmaker(bind=self.engine)()