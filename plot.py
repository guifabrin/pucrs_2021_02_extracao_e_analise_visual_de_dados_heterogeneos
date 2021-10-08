# Copyright 2021, MetaQuotes Ltd.
# https://www.mql5.com
import random
from datetime import datetime

import MetaTrader5 as mt5
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import mongodb
from args import parse
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.dates as mpl_dates

register_matplotlib_converters()
args = parse()
print('mt5 initializing')
if not mt5.initialize():
    mt5.shutdown()
print('mt5 initialized, init copy {} {} {} {}'.format(args.tick, args.mt5_timeframe, args.since, args.until))
ticks = mt5.copy_rates_range(args.tick, args.mt5_timeframe, args.since, args.until)
ticks_frame = pd.DataFrame(ticks)
ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')
print('copy done, adding dates not found with frequency {}'.format(args.panda_frequency))
s = pd.Series(ticks['close'], ticks_frame['time'])
frequency_result = s.asfreq(args.panda_frequency)
ohlc = ticks_frame.loc[:, ['time', 'open', 'high', 'low', 'close']]
ohlc['time'] = ticks_frame['time']
ohlc['time'] = ohlc['time'].apply(mpl_dates.date2num)
ohlc = ohlc.astype(float)
fign = make_subplots(specs=[[{"secondary_y": True}]])
dates = frequency_result._data.items
fign.add_trace(go.Candlestick(x=ticks_frame['time'],
                              open=ohlc['open'],
                              high=ohlc['high'],
                              low=ohlc['low'],
                              close=ohlc['close'],
                              name="Stock price " + args.tick + " with timeframe " + args.str_timeframe),
               secondary_y=False)
results = mongodb.count_in_dates(args.query, args.since, args.until, dates)
fign.add_trace(go.Scatter(x=dates, y=results, name="Tweet count with query '" + args.query + "'"), secondary_y=True)
#
for key, value in args.lines.items():
    random_byte = lambda: random.randint(0, 255)
    color = '#%02X%02X%02X' % (random_byte(), random_byte(), random_byte())
    date_time_event = datetime.strptime(key, '%Y-%m-%d %H:%M:%S')
    fign.add_trace(go.Scatter(x=[date_time_event, date_time_event], y=[0, max(filter(lambda f:f, results))], name=value,
                              line=dict(color=color, width=1, dash='dash')), secondary_y=True)
fign.update_layout(
    title_text="Quantitative comparative into tweet count using query '" + args.query + "' and stock price " + args.tick + " and timeframe " + args.str_timeframe)
fign.write_html(args.filename() + ".html")
if args.show:
    fign.show()
mt5.shutdown()
