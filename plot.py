# Copyright 2021, MetaQuotes Ltd.
# https://www.mql5.com
import argparse
from datetime import datetime

import MetaTrader5 as mt5
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
import pandas as pd
from mpl_finance import candlestick_ohlc
from pandas.plotting import register_matplotlib_converters
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import time

from databases import mongodb

engine = create_engine("mysql+pymysql://root:@localhost/mt5_twitter?charset=utf8mb4")
session = Session(bind=engine)

register_matplotlib_converters()

ap = argparse.ArgumentParser()

# Add the arguments to the parser
ap.add_argument("-t", "--tick", required=True, help="tick to generate first part of the chart")
ap.add_argument("-c", "--count", required=True, help="max ticks count")
ap.add_argument("-q", "--query", required=True, help="query to search into database")
ap.add_argument("-s", "--since", required=True, help="since date")
ap.add_argument("-u", "--until", required=True, help="until date")
ap.add_argument("-f", "--frame", required=True, help="frame data from mt5 lib like TIMEFRAME_H1")
ap.add_argument("-p", "--path", required=True, help="path to save generated image")
ap.add_argument("-d", "--database", required=True, help="database to retrive data")

ap.add_argument("-m", "--favorite", required=False, help="favorite multiplier")
ap.add_argument("-r", "--retweets", required=False, help="retweets multiplier")

args = vars(ap.parse_args())
tick = args['tick']
query = args['query']
count = args['count']
since = datetime.strptime(args['since'], '%Y-%m-%d %H:%M:%S')
until = datetime.strptime(args['until'], '%Y-%m-%d %H:%M:%S')
timeframe = getattr(mt5, args['frame'])
str_timeframe = args['frame'].split('_')[1]
panda_frequency = str_timeframe[0]
path_img = args['path']
database = args['database']
favorite_multiplier = None
retweets_multiplier = None
if args['favorite']:
    favorite_multiplier = int(args['favorite'])
    retweets_multiplier = int(args['retweets'])

print('mt5 initializing')
if not mt5.initialize():
    mt5.shutdown()
print('mt5 initialized, init copy {} {} {} {}'.format(tick, timeframe, since, until))
ticks = mt5.copy_rates_range(tick, timeframe, since, until)
ticks_frame = pd.DataFrame(ticks)
ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')
fig, axs = plt.subplots(2, sharex='all')
fig.suptitle('{} x twitter count about "{}" from {} to {} in timeframe {} with importance {}vs{}'.format(
    tick,
    query,
    since.isoformat().split('T')[0],
    until.isoformat().split('T')[0],
    str_timeframe,
    favorite_multiplier if favorite_multiplier else '0',
    retweets_multiplier if retweets_multiplier else '0'
))
print('copy done, adding dates not found with frequency {}'.format(panda_frequency))
s = pd.Series(ticks['close'], ticks_frame['time'])
frequency_result = s.asfreq(panda_frequency)

ohlc = ticks_frame.loc[:, ['time', 'open', 'high', 'low', 'close']]
ohlc['time'] = ticks_frame['time']
ohlc['time'] = ohlc['time'].apply(mpl_dates.date2num)
ohlc = ohlc.astype(float)

candlestick_ohlc(axs[0], ohlc.values, width=0.01, colorup='green', colordown='red', alpha=0.8)

dates = frequency_result._data.items

results = mongodb.count_in_dates(query, since, until, dates, favorite_multiplier, retweets_multiplier)

axs[1].plot(dates, results, 'r-')
figure = plt.gcf()
figure.set_size_inches(12, 10)
filename = '{}_{}_{}_{}_{}_{}_{}_{}'.format(
    tick,
    query,
    since.isoformat().split('T')[0],
    until.isoformat().split('T')[0],
    str_timeframe,
    int(time.time()),
    favorite_multiplier if favorite_multiplier else '0',
    retweets_multiplier if retweets_multiplier else '0'
)
fig.savefig(path_img + "\\" + filename)  # save the figure to file
plt.xticks(rotation=90)
plt.show()
mt5.shutdown()
