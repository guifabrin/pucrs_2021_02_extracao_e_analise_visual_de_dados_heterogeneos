import datetime
import os

import pandas as pd
import random

model = 'python ..\\..\\src\\fetch.py -q {} -s {} -u {} -t 12'
items = [
    {
        'query': 'petrobras',
        'date_init': datetime.date(2014, 1, 1),
        'date_end': datetime.date.today()
    },
    {
        'query': 'mariana',
        'date_init': datetime.date(2015, 10, 1),
        'date_end': datetime.date(2015, 11, 1)
    },
    {
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
    month_list = [i.date() for i in pd.date_range(start=item['date_init'], end=item['date_end'], freq='MS')]
    for date_init in month_list:
        lines.append(
            model.format(
                item['query'],
                date_init.isoformat().split('T')[0],
                last_day_of_month(date_init).isoformat().split('T')[0],
            )
        )

random.shuffle(lines)

total_files = 10
total_per_file = len(lines) / total_files
filenames = []
path_bat = os.path.abspath("./scripts/bat/")
fetch_filename = '{}\\fetch.bat'.format(path_bat)
path_bat_partials = os.path.abspath("{}/partials/".format(path_bat))
line_index = 0
for i in range(0, total_files):
    filename = "{}\\fetch_{}.bat".format(path_bat_partials, str(i))
    f = open(filename, "w")
    while line_index < total_per_file * (i+1):
        f.write(lines[line_index]+'\n')
        line_index += 1
    f.close()
    filenames.append(os.path.relpath(filename, fetch_filename+'\\..\\'))

f = open(fetch_filename, "w")
for filename in filenames:
    f.write('start '+filename + '\n')
f.close()
