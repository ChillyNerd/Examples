from db.abstract_db import AbstractDB
from db.schema.users import UsersSchema
from db.schema.base import base
from utils.config import Config
import cx_Oracle
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


class DB(AbstractDB):
    users_schema: UsersSchema

    def __init__(self, config: Config):
        if config.use_external_oracle:
            cx_Oracle.init_oracle_client(config.external_oracle_path)
        dsn = cx_Oracle.makedsn(config.db_host, config.db_port, service_name=config.db_name)
        connection_string = f'oracle+cx_oracle://{config.db_user}:{config.db_pass}@{dsn}'
        self.engine = create_engine(connection_string, max_identifier_length=128, pool_pre_ping=True, pool_size=20,
                                    max_overflow=0)
        self.session_maker = sessionmaker(autocommit=False, autoflush=False, bind=self.engine, expire_on_commit=False)
        self.prepare()

    def get_session(self) -> Session:
        return self.session_maker()

    def prepare(self):
        self.users_schema = UsersSchema(self)
        base.metadata.create_all(self.engine)
