from datetime import datetime

from sql_formatter.core import format_sql
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


def count_in_dates(query, since, until, dates):
    len_dates = len(dates)
    groups = ''
    print('mounting sql query')
    for i in range(len_dates - 1):
        dt_init = datetime.combine(dates[i].date(), dates[i].time())
        dt_end = datetime.combine(dates[i + 1].date(), dates[i + 1].time())
        groups += " when `datetime` between \"{}\" and \"{}\"" \
                  "    then {}".format(dt_init.isoformat(), dt_end.isoformat(), i)
    sql = "select " \
          "case " \
          "    {} " \
          "else {} " \
          "end as date_group, count(*) from tweets where lower(content) like lower('%%{}%%') " \
          "and `datetime` BETWEEN \"{}\" and \"{}\" group by date_group ".format(groups, len_dates - 1, query,
                                                                                 since.isoformat().split('T')[0],
                                                                                 until.isoformat().split('T')[0])
    print('sql query mounted')
    print(format_sql(sql))
    print('fetching')
    rows = []
    with engine.connect() as con:
        rs = con.execute(format_sql(sql))
        for row in rs:
            rows.append(row)

    print('fetched, mounting second chart')
    results = []
    for i in range(len_dates):
        results.append(None)
    for i in range(len(rows)):
        results[rows[i][0]] = rows[i][1]
    print('finishing')
    return results
