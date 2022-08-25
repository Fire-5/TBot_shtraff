import sqlalchemy as sa
import numpy as np
import os
import enum

from detection import detect
from .db_session import SqlAlchemyBase, create_session

# class Role(enum.Enum):
#     pups_default = enum.auto()
#     programmist_python = enum.auto()
#     programmist_winform = enum.auto()
#     programmist_backend = enum.auto()
#     programmist_unity_2d = enum.auto()
#     programmist_unity_3d = enum.auto()
#     programmist_unity_VR = enum.auto()
#     programmist_unity_AR = enum.auto()
#     programmist_mobile = enum.auto()
#     designer_2d = enum.auto()
#     designer_3d = enum.auto()
#     designer_frontend = enum.auto()
#     advertiser = enum.auto()
#     operator = enum.auto()
#     curator = enum.auto()
#     mentor = enum.auto()
#     expert = enum.auto()


# Many-to-many relationship: https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#many-to-many
# Как добавить новые поля к записи many-to-many: https://stackoverflow.com/a/62378982/774971 , где дан ответ:
# https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html#association-object


class Pups(SqlAlchemyBase):
    __tablename__ = 'pups'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    username = sa.Column(sa.String, nullable=False, unique=False)
    firma = sa.Column(sa.String, nullable=True, default='Нет фирмы')
    role = sa.Column(sa.String, nullable=True, default='Не распределено')
    descriptors = sa.Column(sa.BLOB, nullable=False, unique=True)

    def new(self):
        # TODO: Дописать функцию, для добавления пользователя в БД.
        session = create_session()

        obama_desc = detect(f'{os.getcwd()}//test//obama.jpg')
        np_obama_desc = np.array(obama_desc)
        # print(type(np_obama_desc), '\n', np_obama_desc)
        session.add(self.Pups(username=f'{}',
                              role=f'{}',
                              firma=f'{}',
                              descriptors=obama_desc))
        session.commit()

    def __repr__(self):
        return f'Pups {self.id}:{self.username}, {self.role}'
