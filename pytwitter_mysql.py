# Copyright 2021, MetaQuotes Ltd.
# https://www.mql5.com
from datetime import datetime
import MetaTrader5 as mt5
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from models import Tweet

engine = create_engine("mysql+pymysql://root:@localhost/mt5_twitter?charset=utf8mb4")
session = Session(bind=engine)

register_matplotlib_converters()
tick = "VALE3"
query = 'brumadinho'
count = 1000000
date_init = datetime(2019, 1, 1)
date_end = datetime(2021, 12, 31)

if not mt5.initialize():
    mt5.shutdown()
ticks = mt5.copy_rates_range(tick, mt5.TIMEFRAME_H1, date_init, date_end)
ticks_frame = pd.DataFrame(ticks)
ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')
fig, axs = plt.subplots(2, sharex='all')
fig.suptitle(tick + ' x twitter counts')
axs[0].plot(ticks_frame['time'], ticks['close'], 'b-', label=tick)
count = []
length = (len(ticks_frame['time']) - 1)
j = 0
for i in range(length):
    dt_init = datetime.combine(ticks_frame['time'][i].date(), ticks_frame['time'][i].time())
    dt_end = datetime.combine(ticks_frame['time'][i + 1].date(), ticks_frame['time'][i + 1].time())
    count.append(
        session.\
            query(Tweet).\
            filter(Tweet.content.contains(query)).\
            filter(Tweet.datetime.between(dt_init, dt_end)).count())

count.append(0)
axs[1].plot(ticks_frame['time'], count, 'r-', label='twitter count about ' + query)
figure = plt.gcf()
figure.set_size_inches(12, 10)
plt.xticks(rotation=90)
plt.show()
mt5.shutdown()
