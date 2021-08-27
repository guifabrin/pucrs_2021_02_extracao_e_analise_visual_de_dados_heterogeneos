# Copyright 2021, MetaQuotes Ltd.
# https://www.mql5.com
from datetime import datetime
import MetaTrader5 as mt5
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sql_formatter.core import format_sql
import argparse


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

print('mt5 initializing')
if not mt5.initialize():
    mt5.shutdown()
print('mt5 initialized, init copy {} {} {} {}'.format(tick, timeframe, since, until))
ticks = mt5.copy_rates_range(tick, timeframe, since, until)
ticks_frame = pd.DataFrame(ticks)
ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')
fig, axs = plt.subplots(2, sharex='all')
fig.suptitle('{} x twitter count about "{}" from {} to {} in timeframe {}'.format(
    tick,
    query,
    since.isoformat().split('T')[0],
    until.isoformat().split('T')[0],
    str_timeframe
))
print('copy done, adding dates not found with frequency {}'.format(panda_frequency))
s = pd.Series(ticks['close'], ticks_frame['time'])
frequency_result = s.asfreq(panda_frequency)
axs[0].plot(frequency_result)
dates = frequency_result._data.items

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
        "and `datetime` BETWEEN \"{}\" and \"{}\" group by date_group ".format(groups, len_dates-1, query, since.isoformat().split('T')[0], until.isoformat().split('T')[0])
print('sql query mounted')

print('fetching')
rows = []
with engine.connect() as con:
    rs = con.execute(format_sql(sql))
    for row in rs:
        rows.append(row)

print('fetched, mounting second chart')
count = []
for i in range(len_dates):
    try:
        count.append(rows[i][1])
    except:
        count.append(None)
print('finishing')

axs[1].plot(dates, count, 'r-')
figure = plt.gcf()
figure.set_size_inches(12, 10)
filename = '{}_{}_{}_{}_{}'.format(
    tick,
    query,
    since.isoformat().split('T')[0],
    until.isoformat().split('T')[0],
    str_timeframe
)
fig.savefig(path_img + filename)  # save the figure to file
plt.xticks(rotation=90)
plt.show()
mt5.shutdown()
