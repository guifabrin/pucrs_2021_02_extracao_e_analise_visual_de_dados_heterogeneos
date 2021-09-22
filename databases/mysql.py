from datetime import datetime

from sql_formatter.core import format_sql
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Tweet

from dotenv import dotenv_values
config = dotenv_values(".env")

engine = create_engine(config["MYSQL_URL"])


def store(tweet):
    session = Session(bind=engine)
    try:
        if session.query(Tweet).filter(Tweet.id == tweet.id).count() == 0:
            session.add(tweet)
            session.commit()
        return 1
    except Exception as ex:
        session.rollback()
        return 0


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


def get_query_id(query):
    if query == "petrobras":
        return 0
    if query == "brumadinho":
        return 1
    if query == "renner":
        return 2
