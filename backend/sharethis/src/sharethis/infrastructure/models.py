from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeMeta


Base: DeclarativeMeta = declarative_base()


class ContentMeta(Base):
    __tablename__ = 'content_meta'

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    encryption_method = Column(String)

    def __init__(self, *args, **kwargs):
        super(ContentMeta, self).__init__(*args, **kwargs)
