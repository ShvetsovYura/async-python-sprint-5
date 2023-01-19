from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from db.db import Base


class UserModel(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)    # noqa A003
    name = Column(String(100), unique=True, index=True)
    hashed_password = Column(String())
    is_active = Column(
        Boolean(),
        default=True,
        nullable=False,
    )

    files = relationship('FileModel', back_populates='user', passive_deletes=True)


class FileModel(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)    # noqa A003
    name = Column(String(50))
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
    subpath = Column(String(100))
    size = Column(Integer)
    is_downloadable = Column(Boolean)
    author = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user = relationship('UserModel', back_populates='files')
    UniqueConstraint("name", "path", name="uix_subpaths")    # noqa CCE0002
