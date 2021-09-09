import pymongo

client = pymongo.MongoClient("mongodb+srv://root:mongodb2021@localhost:27017/database?retryWrites=true&w=majority")
db = client.test
db = client['mt5_twitter']
collection_currency = db['tweets']


def store(tweet):
    collection_currency.insert_one(tweet.__dict__)
