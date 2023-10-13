from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
import lib.mylog.orm as ormlog

class ORMInfo:
    '''
    ORMInfo 是設計一個通用的 ORM 設定物件，好讓 ORMDriver 物件可以輕鬆地取得連線資訊。
    '''
    
    def __init__(self, driver: str, host: str, port: int, database: str, account: str, password: str):
        self.driver = driver
        self.host = host
        self.port = port
        self.database = database
        self.account = account
        self.password = password

    @property
    def signature(self) -> str:
        '''
        設計 signature，讓 make_orm 在遇到相同的 ORMInfo 物件時，可以直接從快取取得 ORM 物件。
        因為一個 IP:PORT 連接的是一個資料庫，不會存在兩個不同的資料庫，
        所以這裡使用 host:port 當作 key 來儲存 ORM 物件就可以了
        '''
        return f'{self.host}:{self.port}'
    
class ORM(ABC):
    '''
    ORM 提供兩個功能，一個是建立抽象資料庫物件，透過 SQLAlchemy 與各種資料庫串接。
    另一個是繼承 With 語句，提供一個可以自動關閉的 ORM 連線物件。
    '''
    def __init__(self, conn: ORMInfo, commit_on_exit: bool = True):
        super().__init__()
        self.conn = conn
        self._session: Session = None
        self.commit_on_exit = commit_on_exit
    
    def __enter__(self):
        '''
        __enter__ 如果裡面有 raise Exception，則 __exit__ 會接收到例外物件。
        '''
        self._session = self.connect()
        if self._session is None:
            ormlog.logger.error(f"無法連上資料庫 {self.dsn}...")
            raise Exception(f"無法連上資料庫 {self.dsn}...")

        return self._session
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self._session is None:
            return
        
        # 如果有例外發生，就恢復到 commit 之前的狀態
        if exc_type is not None:
            ormlog.logger.error(f"ORM 發生{exc_type}錯誤，錯誤為「{exc_value}」，回滾資料庫...")
            self._session.rollback()

        #? 想想看怎麼根據語句來決定要不要 commit
        #? 例如 SELECT 語句不要 commit，但 INSERT 語句要
        if self.commit_on_exit:
            self._session.commit()

        self._session.close()

        return True

    @property
    @abstractmethod
    def dsn(self) -> str:
        '''
        實現資料庫連線字串
        '''
        pass

    @abstractmethod
    def connect(self) -> Session:
        pass