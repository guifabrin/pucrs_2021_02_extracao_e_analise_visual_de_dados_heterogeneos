import argparse
import threading

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Tweet
import snscrape.modules.twitter as sntwitter

engine = create_engine("mysql+pymysql://root:@localhost/mt5_twitter?charset=utf8mb4")


def fetch(query, date_init, date_end):
    session = Session(bind=engine)
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(
            query + ' since:' + date_init + ' until:' + date_end).get_items()):
        print('Importing', tweet.tweetID)
        try:
            db_tweet = Tweet()
            db_tweet.id = tweet.tweetID
            db_tweet.user_id = tweet.user_id
            db_tweet.content = tweet.content
            db_tweet.datetime = tweet.date
            db_tweet.favorite_count = tweet.favorite_count
            db_tweet.retweet_count = tweet.retweet_count
            session.add(db_tweet)
            session.commit()
        except Exception as e:
            session.rollback()
            print(e)

ap = argparse.ArgumentParser()

# Add the arguments to the parser
ap.add_argument("-q", "--query", required=True, help="query")
ap.add_argument("-s", "--since", required=True, help="since")
ap.add_argument("-u", "--until", required=True, help="until")
args = vars(ap.parse_args())

fetch(args['query'], args['since'], args['until'])
