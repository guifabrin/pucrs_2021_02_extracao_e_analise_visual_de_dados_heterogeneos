from sqlalchemy import Column, Text, String, Integer, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Tweet(Base):
    __tablename__ = 'tweets'
    i = Column(String, unique=True, primary_key=True)
    d = Column(DateTime)
    f = Column(Integer)
    r = Column(Integer)
    q = Column(Integer)
