from db.schema.base import base
from sqlalchemy.types import Integer, String
from sqlalchemy import Column
from typing import List, Type
from db.abstract_db import AbstractDB


class User(base):
    __tablename__ = 'users'
    __table_args__ = {"schema": "dummy"}
    id = Column(Integer, primary_key=True)
    name = Column(String)


class UsersSchema:
    def __init__(self, db: AbstractDB):
        self.db = db

    def get_users_by_names(self, names: List[str]) -> List[Type[User]]:
        with self.db.get_session() as session:
            return session.query(User).where(User.name.in_(names)).all()
