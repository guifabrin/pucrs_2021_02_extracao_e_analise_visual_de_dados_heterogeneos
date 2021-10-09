import argparse
import os
import sys
import threading
import time
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime, timedelta
from dotenv import dotenv_values

import mongodb
from snscrape.twitter import TwitterSearchScraper

config = dotenv_values(".env")

metrics = {}
workers = {}
start = time.time()
futures = []


def update_progress(progress):
    bar_length = 30  # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(bar_length * progress))
    end = time.time()
    total = end - start
    total_progress = progress * 100
    total_progress = total_progress if total_progress > 0 else 1
    perspective = total * 100 / total_progress
    total = timedelta(seconds=total)
    perspective = timedelta(seconds=perspective)
    text = "\rPercent: [{0}] {1}% {2} {3} {4}; Totals:{5}; Threads:{6}".format("#" * block + "-" * (bar_length - block),
                                                                               total_progress,
                                                                               status, total, perspective, metrics,
                                                                               workers)
    sys.stdout.write(text)
    sys.stdout.flush()
    return progress


def print_metrics():
    while True:
        total = len(futures)
        complete = len(list(filter(lambda b: b, map(lambda f: f.done(), futures))))
        result = 0
        if total > 0:
            result = update_progress(complete / total)
        time.sleep(0.3)
        if result == 1:
            break


threading.Thread(target=print_metrics, args=()).start()


def update_metrics(method):
    if method not in metrics:
        metrics[method] = 0
    metrics[method] += 1


def update_workers(method, value):
    if method not in workers:
        workers[method] = 0
    workers[method] += value


def twint_callback(tweet, query_id):
    mongodb.store({
        'i': tweet['id_str'],
        'q': query_id,
        'd': datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y').timestamp(),
        'f': tweet['favorite_count'],
        'r': tweet['retweet_count']
    })
    update_metrics('twint')


def worker_snscrape(query, date_init, date_end):
    update_workers('snscrape', 1)
    try:
        log_filename = "logs\\fetcher_" + query + ".txt"
        if not os.path.exists(log_filename):
            log_file = open(log_filename, "a+")
            log_file.write("")
            log_file.close()
        lines = open(log_filename, "r").read().split('\n')
        if date_init in lines:
            print('Skipping ' + date_init)
            update_workers('snscrape', -1)
            return
        total = 0
        query_id = mongodb.get_query_id(query)
        for i, tweet in enumerate(TwitterSearchScraper(
                query + ' since:' + date_init + ' until:' + date_end).get_items()):
            total += mongodb.store({
                'i': tweet.tweetID,
                'q': query_id,
                'd': tweet.date.timestamp(),
                'f': tweet.favorite_count,
                'r': tweet.retweet_count
            })
            update_metrics('snscrape')
            if total == 0:
                log_file = open(log_filename, "a+")
                log_file.write(date_init+"\n")
                log_file.close()
    except Exception as ex:
        print(ex)
    update_workers('snscrape', -1)


class Options:
    pass


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-q", "--query", required=True, help="query")
    ap.add_argument("-s", "--since", required=True, help="since")
    ap.add_argument("-u", "--until", required=False, help="until")
    ap.add_argument("-t", "--threads", required=True, help="threads")
    args = vars(ap.parse_args())
    start_date = datetime.fromisoformat(args['since'])
    if args['until']:
        end_date = datetime.fromisoformat(args['until'])
    else:
        end_date = start_date + timedelta(days=1)
    delta = end_date - start_date
    days = 1

    with ThreadPoolExecutor(max_workers=int(args['threads'])) as executor:
        for i in range(delta.days + days):
            date_init = (start_date + timedelta(days=i)).isoformat()
            date_end = (start_date + timedelta(days=i + days)).isoformat()
            futures.append(executor.submit(worker_snscrape, args['query'], date_init, date_end))
