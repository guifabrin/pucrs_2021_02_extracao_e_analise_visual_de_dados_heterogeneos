from sqlalchemy import Column, Text, String, Integer, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Tweet(Base):
    __tablename__ = 'tweets'
    id = Column(String, unique=True, primary_key=True)
    user_id = Column(String)
    content = Column(Text)
    datetime = Column(DateTime)
    favorite_count = Column(Integer)
    retweet_count = Column(Integer)
