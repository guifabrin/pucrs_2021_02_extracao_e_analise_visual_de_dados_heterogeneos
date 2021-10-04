# Copyright 2021, MetaQuotes Ltd.
# https://www.mql5.com
import MetaTrader5 as mt5
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
import pandas as pd
from mpl_finance import candlestick_ohlc
from pandas.plotting import register_matplotlib_converters
from helpers.args import parse
from databases import mongodb

register_matplotlib_converters()
args = parse()
print('mt5 initializing')
if not mt5.initialize():
    mt5.shutdown()
print('mt5 initialized, init copy {} {} {} {}'.format(args.tick, args.mt5_timeframe, args.since, args.until))
ticks = mt5.copy_rates_range(args.tick, args.mt5_timeframe, args.since, args.until)
ticks_frame = pd.DataFrame(ticks)
ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')
fig, axs = plt.subplots(2, sharex='all')
fig.suptitle(args.subtitle)
print('copy done, adding dates not found with frequency {}'.format(args.panda_frequency))
s = pd.Series(ticks['close'], ticks_frame['time'])
frequency_result = s.asfreq(args.panda_frequency)
ohlc = ticks_frame.loc[:, ['time', 'open', 'high', 'low', 'close']]
ohlc['time'] = ticks_frame['time']
ohlc['time'] = ohlc['time'].apply(mpl_dates.date2num)
ohlc = ohlc.astype(float)
candlestick_ohlc(axs[0], ohlc.values, width=0.01, colorup='green', colordown='red', alpha=0.8)
dates = frequency_result._data.items
results = mongodb.count_in_dates(args.query, args.since, args.until, dates, args.favorite_multiplier, args.retweets_multiplier)
axs[1].plot(dates, results, 'r-')
figure = plt.gcf()
figure.set_size_inches(12, 10)
fig.savefig(args.filename())
plt.xticks(rotation=90)
if args.show:
    plt.show()
mt5.shutdown()
