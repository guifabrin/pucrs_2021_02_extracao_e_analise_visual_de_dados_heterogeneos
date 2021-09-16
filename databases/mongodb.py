import json
from datetime import datetime

import pymongo
from sqlalchemy.ext.declarative import DeclarativeMeta


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data)  # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)


client = pymongo.MongoClient(
    "mongodb://root:mongodb2021@localhost/database?retryWrites=true&w=majority&authSource=admin")
db = client['mt5_twitter']
collection_currency = db['tweets']


def store(tweet):
    tweet.datetime = tweet.datetime.timestamp()
    if collection_currency.find_one({"id": tweet.id}):
        print('Tweet with id {} already stored'.format(tweet.id))
        return
    collection_currency.insert_one(json.loads(json.dumps(tweet, cls=AlchemyEncoder)))
    print('Tweet with id {} stored'.format(tweet.id))


def store_many(tweets):
    for tweet in tweets:
        store(tweet)


def count_in_dates(query, since, until, dates):
    results = []
    len_dates = len(dates)
    for i in range(len_dates):
        results.append(None)
    print('mounting sql query')
    for i in range(len_dates - 1):
        dt_init = datetime.combine(dates[i].date(), dates[i].time())
        dt_end = datetime.combine(dates[i + 1].date(), dates[i + 1].time())

        size = len(
            list(collection_currency.find({
                "$and": [
                    {"datetime": {"$gt": dt_init.timestamp(), "$lt": dt_end.timestamp()}},
                    {"content": {"$regex": query}}
                ]
            })))
        results[i] = size if size > 0 else None
    return results
