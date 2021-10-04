# Copyright 2021, MetaQuotes Ltd.
# https://www.mql5.com

import MetaTrader5 as mt5
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
import pandas as pd
from mpl_finance import candlestick_ohlc
from pandas.plotting import register_matplotlib_converters
from databases import mongodb
from helpers.args import parse
register_matplotlib_converters()
args = parse()
print('mt5 initializing')
if not mt5.initialize():
    mt5.shutdown()
print('mt5 initialized, init copy {} {} {} {}'.format(args.tick, args.mt5_timeframe, args.since, args.until))
ticks = mt5.copy_rates_range(args.tick, args.mt5_timeframe, args.since, args.until)
ticks_frame = pd.DataFrame(ticks)
ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')
fig, ax1 = plt.subplots()
fig.suptitle(args.subtitle)
print('copy done, adding dates not found with frequency {}'.format(args.panda_frequency))
s = pd.Series(ticks['close'], ticks_frame['time'])
frequency_result = s.asfreq(args.panda_frequency)

ohlc = ticks_frame.loc[:, ['time', 'open', 'high', 'low', 'close']]
ohlc['time'] = ticks_frame['time']
ohlc['time'] = ohlc['time'].apply(mpl_dates.date2num)
ohlc = ohlc.astype(float)

candlestick_ohlc(ax1, ohlc.values, width=0.01, colorup='green', colordown='red', alpha=0.8)

dates = frequency_result._data.items
results = mongodb.count_in_dates(args.query, args.since, args.until, dates, args.favorite_multiplier, args.retweets_multiplier)
ax2 = ax1.twinx()
color = 'tab:blue'
ax2.set_ylabel('tweet count', color=color)
ax2.plot(dates, results, color=color)
ax2.tick_params(axis='y', labelcolor=color)
fig.tight_layout()
figure = plt.gcf()
figure.set_size_inches(12, 10)
fig.savefig(args.filename('_both'))
plt.xticks(rotation=90)
if args.show:
    plt.show()
mt5.shutdown()
