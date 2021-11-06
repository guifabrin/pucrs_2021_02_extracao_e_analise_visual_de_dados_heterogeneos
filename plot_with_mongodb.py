import datetime
import subprocess
import pandas as pd
import time

model = 'python .\\src\\plot.py -t {} -q {} -s "{} 00:00:00" -u "{} 23:59:59" -f {} -j "{}"'
timeframes = ['TIMEFRAME_H1', 'TIMEFRAME_M30', 'TIMEFRAME_M15', 'TIMEFRAME_D1',  'TIMEFRAME_M1']
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
                ) + ' -i "{f}*1+{r}*0.1;{f}*5;{r}*5" -d mongodb'
            )
start = time.time()
for line in lines:
    subprocess.call(line, shell=True)
end = time.time()
print(f"MongoDB: Runtime of the program is {end - start}")
