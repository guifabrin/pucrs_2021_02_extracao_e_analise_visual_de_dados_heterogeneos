import argparse

from store import mongodb, mysql
from fetch.twitter import fetch
from datetime import date, timedelta

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    # Add the arguments to the parser
    ap.add_argument("-q", "--query", required=True, help="query")
    ap.add_argument("-s", "--since", required=True, help="since")
    ap.add_argument("-u", "--until", required=True, help="until")
    ap.add_argument("-m", "--method", required=True, help="until")
    args = vars(ap.parse_args())
    if args['method'] == 'mysql':
        fetch(args['query'], args['since'], args['until'], mysql.store)
    if args['method'] == 'mongodb':
        fetch(args['query'], args['since'], args['until'], mongodb.store)
else:
    start_date = date(2021, 9, 1)
    end_date = date(2021, 9, 30)
    store_method = mongodb.store #mysql.store

    delta = end_date - start_date
    for i in range(delta.days + 1):
        start_day = (start_date + timedelta(days=i)).isoformat()
        day = (start_date + timedelta(days=i + 1)).isoformat()
        try:
            fetch('petrobras', start_day, day)
        except Exception as ex:
            print(ex)
            pass
        try:
            fetch('petrobras', start_day, day)
        except Exception as ex:
            print(ex)
            pass
        try:
            fetch('renner', start_day, day)
        except Exception as ex:
            print(ex)
            pass