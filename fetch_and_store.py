import argparse
import sys
import threading
import time
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime, timedelta

import tweepy
from dotenv import dotenv_values

from libs import twint
from libs.OMGOT.GetOldTweets3.cli import main
from libs.snscrape.modules.twitter import TwitterSearchScraper

from databases import mongodb, mysql

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


def print_metrics():
    while True:
        total = len(futures)
        complete = len(list(filter(lambda b: b, map(lambda f: f.done(), futures))))
        if total > 0:
            update_progress(complete / total)
        time.sleep(0.3)


threading.Thread(target=print_metrics, args=()).start()


def update_metrics(method):
    if method not in metrics:
        metrics[method] = 0
    metrics[method] += 1


def update_workers(method, value):
    if method not in workers:
        workers[method] = 0
    workers[method] += value


def twint_callback(tweet, query_id, method):
    method.store({
        'i': tweet['id_str'],
        'q': query_id,
        'd': datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y').timestamp(),
        'f': tweet['favorite_count'],
        'r': tweet['retweet_count']
    })
    update_metrics('twint')


def worker_twint(query, date_init, date_end, method):
    update_workers('twint', 1)
    try:
        c = twint.Config()
        c.Since = ' '.join(date_init.split('T'))
        c.Until = ' '.join(date_end.split('T'))
        c.Search = [query]
        c.Limit = 100000
        c.Hide_output = True
        query_id = method.get_query_id(query)
        twint.run.Search(c, lambda tweet: twint_callback(tweet, query_id, method))
    except:
        pass
    update_workers('twint', -1)


def worker_snscrape(query, date_init, date_end, method):
    update_workers('snscrape', 1)
    try:
        query_id = method.get_query_id(query)
        for i, tweet in enumerate(TwitterSearchScraper(
                query + ' since:' + date_init + ' until:' + date_end).get_items()):
            method.store({
                'i': tweet.tweetID,
                'q': query_id,
                'd': tweet.date.timestamp(),
                'f': tweet.favorite_count,
                'r': tweet.retweet_count
            })
            update_metrics('snscrape')
    except:
        pass
    update_workers('snscrape', -1)


def worker_tweepy(query, date_init, date_end, method):
    update_workers('tweepy', 1)
    try:
        auth = tweepy.OAuthHandler(config['TWITTER_CONSUMER_KEY'], config['TWITTER_CONSUMER_SECRET'])
        auth.set_access_token(config['TWITTER_KEY'], config['TWITTER_SECRET'])

        api = tweepy.API(auth)
        query_id = method.get_query_id(query)
        for tweet in tweepy.Cursor(api.search,
                                   q=query,
                                   count=100,
                                   result_type="recent",
                                   since=date_init.split('T')[0],
                                   until=date_end.split('T')[0],
                                   include_entities=True,
                                   lang="pt").items():
            method.store({
                'i': tweet.id,
                'q': query_id,
                'd': tweet.created_at.timestamp(),
                'f': tweet.favorite_count,
                'r': tweet.retweet_count
            })
            update_metrics('tweepy')
    except:
        pass
    update_workers('tweepy', -1)


class Options:
    pass


def worker_get_old(query, date_init, date_end, method):
    update_workers('get_old', 1)
    try:
        options = Options()
        options.search = query
        options.since = date_init.split('T')[0]
        options.until = date_end.split('T')[0]
        options.username = None
        options.userlist = None
        options.members_list = None
        options.all = None
        options.output = None
        options.csv = None
        options.json = None
        options.backoff_exponent = 3.0
        options.min_wait_time = 15
        options.pandas_clean = None
        options.userid = None
        options.geo = None
        options.location = None
        options.near = None
        options.lang = None
        options.elasticsearch = None
        options.year = None
        options.email = None
        options.phone = None
        options.verified = None
        options.hashtags = None
        options.cashtags = None
        options.limit = None
        options.count = None
        options.stats = None
        options.database = None
        options.to = None
        options.essid = None
        options.format = None
        options.user_full = None
        options.profile_full = None
        options.pandas_type = None
        options.index_tweets = None
        options.index_follow = None
        options.index_users = None
        options.debug = None
        options.resume = None
        options.images = None
        options.videos = None
        options.media = None
        options.replies = None
        options.proxy_host = None
        options.proxy_port = None
        options.proxy_type = None
        options.tor_control_port = None
        options.tor_control_password = None
        options.retweets = None
        options.custom_query = None
        options.popular_tweets = None
        options.skip_certs = None
        options.hide_output = True
        options.native_retweets = None
        options.min_likes = None
        options.min_retweets = None
        options.min_replies = None
        options.links = None
        options.source = None
        options.filter_retweets = None
        options.translate = None
        options.translate_dest = None
        options.favorites = None
        options.following = None
        options.followers = None
        query_id = method.get_query_id(query)

        def process(tweet):
            method.store({
                'i': tweet.id_str,
                'q': query_id,
                'd': datetime.fromisoformat(
                    tweet.datetime.split(' ')[0] + "T" + tweet.datetime.split(' ')[1]).timestamp(),
                'f': tweet.likes_count,
                'r': tweet.retweets_count
            })
            update_metrics('get_old')

        main(options, process)
    except:
        pass
    update_workers('get_old', -1)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-q", "--query", required=True, help="query")
    ap.add_argument("-s", "--since", required=True, help="since")
    ap.add_argument("-u", "--until", required=True, help="until")
    ap.add_argument("-m", "--method", required=True, help="method")
    ap.add_argument("-t", "--threads", required=True, help="threads")
    args = vars(ap.parse_args())
    start_date = datetime.fromisoformat(args['since'])
    end_date = datetime.fromisoformat(args['until'])
    delta = end_date - start_date
    method = eval(args['method'])
    total_threads = int(args['threads'])
    max_workers = int(total_threads / 4)


    def thread_pool_get_old():
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i in range(delta.days + 1):
                date_init = (start_date + timedelta(days=i)).isoformat()
                date_end = (start_date + timedelta(days=i + 1)).isoformat()
                futures.append(executor.submit(worker_get_old, args['query'], date_init, date_end, method))


    def thread_pool_tweepy():
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i in range(delta.days + 1):
                date_init = (start_date + timedelta(days=i)).isoformat()
                date_end = (start_date + timedelta(days=i + 1)).isoformat()
                futures.append(executor.submit(worker_tweepy, args['query'], date_init, date_end, method))


    def thread_pool_snscrape():
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i in range(delta.days + 1):
                date_init = (start_date + timedelta(days=i)).isoformat()
                date_end = (start_date + timedelta(days=i + 1)).isoformat()
                futures.append(executor.submit(worker_snscrape, args['query'], date_init, date_end, method))


    def thread_pool_twint():
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i in range(delta.days + 1):
                date_init = (start_date + timedelta(days=i)).isoformat()
                date_end = (start_date + timedelta(days=i + 1)).isoformat()
                futures.append(executor.submit(worker_twint, args['query'], date_init, date_end, method))


    threading.Thread(target=thread_pool_get_old, args=()).start()
    threading.Thread(target=thread_pool_tweepy, args=()).start()
    threading.Thread(target=thread_pool_snscrape, args=()).start()
    threading.Thread(target=thread_pool_twint, args=()).start()
