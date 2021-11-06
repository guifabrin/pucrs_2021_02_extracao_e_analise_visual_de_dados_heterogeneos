import json
import time
from datetime import datetime

import pymongo
from sqlalchemy.orm import DeclarativeMeta

from src import helper
from src.helper import update_progress, load_config

config = load_config()
client = pymongo.MongoClient(config['MONGO_DB_URL'], tlsAllowInvalidCertificates=True)
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
        return 0
    collection_currency.insert_one(json.loads(json.dumps(tweet, cls=AlchemyEncoder)))
    return 1


def store_all(tweets):
    collection_currency.insert_many(json.loads(json.dumps(tweets, cls=AlchemyEncoder)))


def count_in_dates(query, since, until, dates, importances=None):
    start = time.time()
    results = []
    len_dates = len(dates)
    for i in range(len(importances) + 1):
        results.append([])
        for j in range(len_dates):
            results[i].append(0)
    total_interacions = len_dates
    text = str(query) + ' ' + since.isoformat() + ' ' + until.isoformat()
    total_done = 0
    for i in range(len_dates - 1):
        dt_init = datetime.combine(dates[i].date(), dates[i].time())
        dt_end = datetime.combine(dates[i + 1].date(), dates[i + 1].time())
        data = collection_currency.find(
            {"d": {"$gt": dt_init.timestamp(), "$lt": dt_end.timestamp()}, "q": helper.get_query_id(query)})
        results[0][i] = data.count()
        for item in data:
            imp = 1
            for importance in importances:
                results[imp][i] += eval(importance.replace('{f}', str(item['f'])).replace('{r}', str(item['r'])))
                imp += 1
                update_progress(start, text, total_done / total_interacions)
            update_progress(start, text, total_done / total_interacions)
        total_done += 1
        update_progress(start, text, total_done / total_interacions)
    return results