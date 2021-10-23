# Copyright 2021, MetaQuotes Ltd.
# https://www.mql5.com
import json
import os
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

random_byte = lambda: random.randint(0, 255)

register_matplotlib_converters()
args = parse()
if os.path.exists(args.filename() + ".html"):
    print('Already plotted')
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
                              name="Stock price " + args.tick + " with timeframe " + args.str_timeframe))
results = mongodb.count_in_dates(args.query, args.since, args.until, dates, args.importances)
color = '#%02X%02X%02X' % (random_byte(), random_byte(), random_byte())
fign.add_trace(go.Scatter(x=dates, y=results[0], name="Quantitative", line=dict(color=color, width=1), yaxis="y2"))

colors = [color]
texts = ["Quantitative"]

imp = 1
for importance in args.importances:
    color = '#%02X%02X%02X' % (random_byte(), random_byte(), random_byte())
    colors.append(color)
    text = "IC(f,r)=" + importance
    texts.append(text)
    fign.add_trace(
        go.Scatter(x=dates, y=results[imp], name=text, line=dict(color=color, width=1), yaxis="y" + str(imp + 2)))
    imp += 1

for key, value in args.lines.items():
    color = '#%02X%02X%02X' % (random_byte(), random_byte(), random_byte())
    date_time_event = datetime.strptime(key, '%Y-%m-%d %H:%M:%S')
    if args.since <= date_time_event <= args.until:
        fign.add_trace(go.Scatter(x=[date_time_event, date_time_event], y=[0, 1], name=value,
                                  line=dict(color=color, width=1, dash='dash'), yaxis="y" + str(imp + 2)))
fign.update_layout(
    title_text="Quantitative comparative into tweet count using query '" + args.query + "' and stock price " + args.tick + " and timeframe " + args.str_timeframe)

multiplier = 0.08
fign.update_layout(
    xaxis=dict(
        domain=[multiplier * 4, 1]
    ),
    yaxis2=dict(
        title=texts[0],
        anchor="free",
        side="left",
        color=colors[0],
        position=0,
        overlaying="y",
    ),
    yaxis3=dict(
        title=texts[1],
        anchor="free",
        side="left",
        color=colors[1],
        position=multiplier,
        overlaying="y",
    ),
    yaxis4=dict(
        title=texts[2],
        anchor="free",
        side="left",
        color=colors[2],
        position=multiplier * 2,
        overlaying="y",
    ),
    yaxis5=dict(
        title=texts[3],
        anchor="free",
        side="left",
        color=colors[3],
        position=multiplier * 3,
        overlaying="y",
    ),
    yaxis6=dict(
        visible=False,
        overlaying="y",
    ),
)

initial_apply = 1000
total_apply = initial_apply
quantity = 0
last_value = 0
values = frequency_result._data.arrays[0]
operations = []


def buy(date, val, qtd):
    global total_apply, quantity, last_value
    operations.append({
        'data':date.timestamp(),
        'type':'BUY',
        'quantity': qtd,
        'value': val
    })
    total_apply -= val * qtd
    quantity += qtd
    last_value = val


def sell(date, val, qtd):
    global total_apply, quantity, last_value
    operations.append({
        'data':date.timestamp(),
        'type':'SELL',
        'quantity': qtd,
        'value': val
    })
    total_apply += val * qtd
    quantity -= qtd
    last_value = val


qtd_base = 100
last_result = 1
last_date = 0

for index in range(0, len(results[0])):
    result = results[0][index]
    date = dates[index]
    value = values[index]
    if value > 0 and result > 0:
        if last_result > result:
            buy(date, value, qtd_base)
        else:
            sell(date, value, qtd_base)
        last_result = result
        last_date = date

if quantity > 0:
    sell(last_date, last_value, abs(quantity))
else:
    buy(last_date, last_value, abs(quantity))

with open(args.filename() + ".json", 'w') as outfile:
    data = {}
    data['operations'] = operations
    data['initial_apply'] = initial_apply
    data['total_apply'] = total_apply
    json.dump(data, outfile)

fign.write_html(args.filename() + ".html")
if args.show:
    fign.show()
mt5.shutdown()
