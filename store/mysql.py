from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Tweet

engine = create_engine("mysql+pymysql://root:@localhost/mt5_twitter?charset=utf8mb4")

def store(tweet):
    session = Session(bind=engine)
    db_tweet = Tweet()
    db_tweet.id = tweet.tweetID
    db_tweet.user_id = tweet.user_id
    db_tweet.content = tweet.content
    db_tweet.datetime = tweet.date
    db_tweet.favorite_count = tweet.favorite_count
    db_tweet.retweet_count = tweet.retweet_count
    session.add(db_tweet)
    session.commit()