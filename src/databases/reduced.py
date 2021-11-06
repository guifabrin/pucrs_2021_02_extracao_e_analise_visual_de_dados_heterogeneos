import time
from datetime import datetime
from os.path import exists

from src import helper

reduced_filename = "./data/reduced/part-v001-o000-r-00000"
reduced_values = {}
if exists(reduced_filename):
    f = open(reduced_filename, "r")
    values = f.read().split('\n')
    for value in values:
        if value:
            key, total = value.split('\t')
            reduced_values[key] = int(total)
    f.close()


def count_in_dates(query, since, until, dates, importances=None):
    global reduced_values
    start = time.time()
    qid = helper.get_query_id(query)
    results = []
    len_dates = len(dates)
    for i in range(len(importances) + 1):
        results.append([])
        for j in range(len_dates):
            results[i].append(0)
    total_interacions = len_dates
    text = str(query) + ' ' + since.isoformat() + ' ' + until.isoformat()
    total_done = 0
    for i in range(len_dates - 1):
        dt_init = datetime.combine(dates[i].date(), dates[i].time())
        dt_end = datetime.combine(dates[i + 1].date(), dates[i + 1].time())
        time_delta = (dt_end - dt_init)
        minutes = time_delta.total_seconds() / 60
        if minutes == 1.0:  # minute
            key = "{}_{}_{}_{}_{}_m_{}_d".format(qid, dt_init.year, dt_init.month, dt_init.day, dt_init.hour,
                                                 dt_init.minute)
            key_f = "{}_{}_{}_{}_{}_m_{}_d".format(qid, dt_init.year, dt_init.month, dt_init.day, dt_init.hour,
                                                   dt_init.minute)
            key_r = "{}_{}_{}_{}_{}_m_{}_d".format(qid, dt_init.year, dt_init.month, dt_init.day, dt_init.hour,
                                                   dt_init.minute)
        elif minutes == 15.0:  # querter
            if 0 <= minutes < 15:
                quarter = 0
            elif 15 <= minutes < 30:
                quarter = 1
            elif 30 <= minutes < 45:
                quarter = 2
            elif 45 <= minutes <= 60:
                quarter = 3
            key = "{}_{}_{}_{}_{}_q_{}_d".format(qid, dt_init.year, dt_init.month, dt_init.day, dt_init.hour, quarter)
            key_f = "{}_{}_{}_{}_{}_q_{}_f".format(qid, dt_init.year, dt_init.month, dt_init.day, dt_init.hour, quarter)
            key_r = "{}_{}_{}_{}_{}_q_{}_r".format(qid, dt_init.year, dt_init.month, dt_init.day, dt_init.hour, quarter)
        elif minutes == 30.0:  # half
            half = 0 if minutes < 30 else 1
            key = "{}_{}_{}_{}_{}_h_{}_d".format(qid, dt_init.year, dt_init.month, dt_init.day, dt_init.hour, half)
            key_f = "{}_{}_{}_{}_{}_h_{}_f".format(qid, dt_init.year, dt_init.month, dt_init.day, dt_init.hour, half)
            key_r = "{}_{}_{}_{}_{}_h_{}_r".format(qid, dt_init.year, dt_init.month, dt_init.day, dt_init.hour, half)
        elif minutes == 60.0:  # hour
            key = "{}_{}_{}_{}_{}_d".format(qid, dt_init.year, dt_init.month, dt_init.day, dt_init.hour)
            key_f = "{}_{}_{}_{}_{}_f".format(qid, dt_init.year, dt_init.month, dt_init.day, dt_init.hour)
            key_r = "{}_{}_{}_{}_{}_r".format(qid, dt_init.year, dt_init.month, dt_init.day, dt_init.hour)
        elif minutes == 1440.0:  # day
            key = "{}_{}_{}_{}_d".format(qid, dt_init.year, dt_init.month, dt_init.day)
            key_f = "{}_{}_{}_{}_f".format(qid, dt_init.year, dt_init.month, dt_init.day)
            key_r = "{}_{}_{}_{}_r".format(qid, dt_init.year, dt_init.month, dt_init.day)
        results[0][i] = reduced_values[key] if key in reduced_values else 0
        value_f = reduced_values[key_f] if key_f in reduced_values else 0
        value_r = reduced_values[key_r] if key_r in reduced_values else 0
        for index_importance in range(0, len(importances)):
            importance = importances[index_importance]
            results[index_importance + 1][i] += eval(
                importance.replace('{f}', str(value_f)).replace('{r}', str(value_r)))
            helper.update_progress(start, text, total_done / total_interacions)
        total_done += 1
        helper.update_progress(start, text, total_done / total_interacions)
    total_done = total_interacions
    helper.update_progress(start, text, total_done / total_interacions)
    return results
