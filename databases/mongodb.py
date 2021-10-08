import json
import pymongo
from datetime import datetime
from sqlalchemy.ext.declarative import DeclarativeMeta
from unidecode import unidecode

from dotenv import dotenv_values

config = dotenv_values(".env")

client = pymongo.MongoClient(config['MONGO_DB_URL'])
db = client[config['MONGO_DB_CLIENT']]
collection_currency = db[config['MONGO_DB_COLLECTION']]


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data)
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            return fields

        return json.JSONEncoder.default(self, obj)


def store(tweet):
    if collection_currency.find_one({"i": tweet['i']}):
        return
    collection_currency.insert_one(json.loads(json.dumps(tweet, cls=AlchemyEncoder)))


def store_all(tweets):
    collection_currency.insert_many(json.loads(json.dumps(tweets, cls=AlchemyEncoder)))


def count_in_dates(query, since, until, dates):
    results = []
    len_dates = len(dates)
    for i in range(len_dates):
        results.append(None)
    for i in range(len_dates - 1):
        dt_init = datetime.combine(dates[i].date(), dates[i].time())
        dt_end = datetime.combine(dates[i + 1].date(), dates[i + 1].time())
        results[i] = collection_currency.find(
            {"d": {"$gt": dt_init.timestamp(), "$lt": dt_end.timestamp()}, "q": get_query_id(query)}).count()
        print(i, 'of', len_dates, results[i])
    return results


def get_query_id(query):
    q = unidecode(query.lower())
    if "petrobras" in q:
        return 0
    if "brumadinho" in q:
        return 1
    if "renner" in q:
        return 2
    if "pandemia" in q:
        return 3
    if "mariana" in q:
        return 4
