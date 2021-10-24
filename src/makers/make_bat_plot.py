import datetime
import os

import pandas as pd
import random

model = 'python ..\\..\\src\\plot.py -t {} -q {} -s "{} 00:00:00" -u "{} 23:59:59" -f {} -j "{}"'
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
                    '..\\..\\extra\\' + item['ticker'] + '_' + item['query'] + '.json'
                ) + ' -i "{f}*1+{r}*0.1;{f}*5;{r}*5"'
            )

random.shuffle(lines)

total_files = 10
total_per_file = len(lines) / total_files
filenames = []
path_bat = os.path.abspath("./scripts/bat/")
plot_filename = '{}\\plot.bat'.format(path_bat)
path_bat_partials = os.path.abspath("{}/partials/".format(path_bat))
os.makedirs(path_bat_partials, exist_ok=True)
line_index = 0
for i in range(0, total_files):
    filename = "{}\\plot_{}.bat".format(path_bat_partials, str(i))
    f = open(filename, "w")
    while line_index < total_per_file * (i + 1):
        f.write(lines[line_index] + '\n')
        line_index += 1
    f.close()
    filenames.append(os.path.relpath(filename, plot_filename+'\\..\\'))

f = open(plot_filename, "w")
for filename in filenames:
    f.write('start ' + filename + '\n')
f.close()
