from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Tweet
import snscrape.modules.twitter as sntwitter

engine = create_engine("mysql+pymysql://root:@localhost/mt5_twitter?charset=utf8mb4")
session = Session(bind=engine)


def fetch(query, date_init, date_end):
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(
            query + ' since:' + date_init + ' until:' + date_end).get_items()):
        print('Importing', tweet.tweetID)
        try:
            db_tweet = Tweet()
            db_tweet.id = tweet.tweetID
            db_tweet.user_id = tweet.user_id
            db_tweet.content = tweet.content
            db_tweet.datetime = tweet.date
            session.add(db_tweet)
            session.commit()
        except Exception as e:
            session.rollback()
            print(e)


if __name__ == '__main__':
    fetch('petrobras', '2010-01-01', '2021-12-31')
