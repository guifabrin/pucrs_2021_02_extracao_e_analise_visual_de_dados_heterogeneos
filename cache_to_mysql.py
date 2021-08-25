from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from os import listdir, remove
from os.path import isfile, join
import json
from datetime import datetime
from models import Tweet

engine = create_engine("mysql+pymysql://root:@localhost/mt5_twitter?charset=utf8mb4", echo=True)
session = Session(bind=engine)

paths = ['./cache/brumadinho/', './cache/petrobras/']
for folder in paths:
    files = [f for f in listdir(folder) if isfile(join(folder, f))]
    for file in files:
        f = open(folder+file,)
        try:
            result = json.load(f)
            tweet = Tweet()
            tweet.id = result['id']
            tweet.user_id = result['user_id']
            tweet.content = result['content']
            tweet.datetime = datetime.strptime(file.split('_')[1].split('.')[0], '%Y%m%d%H%M%S')
            session.add(tweet)
            session.commit()
        except:
            pass
        finally:
            print('Processing', folder+file)
            f.close()
        remove(folder+file)
