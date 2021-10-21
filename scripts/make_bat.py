import datetime
import os

import pandas as pd
import random

model = 'python plot.py -t {} -q {} -s "{} 00:00:00" -u "{} 23:59:59" -f {} -j "{}"'
timeframes = ['TIMEFRAME_D1', 'TIMEFRAME_H1', 'TIMEFRAME_M30', 'TIMEFRAME_M15']
items = [
    {
        'ticker': 'PETR4',
        'query': 'petrobras',
        'date_init': datetime.date(2014, 1, 1),
        'date_end': datetime.date.today()
    },
    {
        'ticker': 'VALE3',
        'query': 'mariana',
        'date_init': datetime.date(2015, 10, 1),
        'date_end': datetime.date(2015, 11, 1)
    },
    {
        'ticker': 'VALE3',
        'query': 'brumadinho',
        'date_init': datetime.date(2019, 1, 1),
        'date_end': datetime.date(2019, 1, 1)
    }
]


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)


lines = []
for item in items:
    for timeframe in timeframes:
        month_list = [i.date() for i in pd.date_range(start=item['date_init'], end=item['date_end'], freq='MS')]
        for date_init in month_list:
            lines.append(
                model.format(
                    item['ticker'],
                    item['query'],
                    date_init.isoformat(),
                    last_day_of_month(date_init).isoformat(),
                    timeframe,
                    '.\\extra\\' + item['ticker'] + '_' + item['query'] + '.json'
                ) + ' -i "{f}*1+{r}*0.1;{f}*5;{r}*5"'
            )

random.shuffle(lines)

total_files = 10
total_per_file = len(lines) / total_files
filenames = []
os.makedirs("partials\\", exist_ok=True)
line_index = 0
for i in range(0, total_files):
    filename = "partials\\plot_{}.bat".format(str(i))
    f = open(filename, "w")
    f.write("cd..\n")
    while line_index < total_per_file * (i+1):
        f.write(lines[line_index]+'\n')
        line_index += 1
    f.close()
    filenames.append(filename)

f = open('plot.bat', "w")
for filename in filenames:
    f.write('start '+filename + '\n')
f.close()