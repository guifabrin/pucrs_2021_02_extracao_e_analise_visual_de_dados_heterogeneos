import argparse
import time
from datetime import datetime, timedelta

from databases import mongodb, mysql
import concurrent.futures
from libs import twint
from libs.snscrape.modules.twitter import TwitterSearchScraper
import tweepy

from dotenv import dotenv_values
config = dotenv_values(".env")
# acessar a aba "Keys and Access Tokens"
# passa o Consumer Key e o Consumer Secret
auth = tweepy.OAuthHandler(config['TWITTER_CONSUMER_KEY'], config['TWITTER_CONSUMER_SECRET'])

# define o token de acesso
# para criar basta clicar em "Create my access token"
# passa o "Access Token" e o "Access Token Secret"
auth.set_access_token(config['TWITTER_KEY'], config['TWITTER_SECRET'])

api = tweepy.API(auth)

metrics = {}

def update_metrics(method):
    if method not in metrics:
        metrics[method] = 0
    metrics[method] += 1
    print(metrics)



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
    c = twint.Config()
    c.Since = ' '.join(date_init.split('T'))
    c.Until = ' '.join(date_end.split('T'))
    c.Search = [query]
    c.Limit = 100000
    query_id = method.get_query_id(query)
    twint.run.Search(c, lambda tweet: twint_callback(tweet, query_id, method))


def worker_snscrape(query, date_init, date_end, method):
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


def worker_tweepy(query, date_init, date_end, method):
    query_id = method.get_query_id(query)
    for tweet in tweepy.Cursor(api.search,
                               q=query,
                               count=100,
                               result_type="recent",
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


from libs.OMGOT.GetOldTweets3.cli import main

class Options:
    pass

def worker_GetOldTweets3(query, date_init, date_end, method):
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
    options.hide_output = None
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

    continuee = True
    def process(tweet):
        global continuee
        method.store({
            'i': tweet.id_str,
            'q': query_id,
            'd': datetime.fromisoformat(tweet.datetime.split(' ')[0]+"T"+tweet.datetime.split(' ')[1]).timestamp(),
            'f': tweet.likes_count,
            'r': tweet.retweets_count
        })
        continuee = False
        update_metrics('get_old')
    tries = 0
    while continuee and tries < 10:
        tries += 1
        main(options, process)
        time.sleep(5)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-q", "--query", required=True, help="query")
    ap.add_argument("-s", "--since", required=True, help="since")
    ap.add_argument("-u", "--until", required=True, help="until")
    ap.add_argument("-m", "--method", required=True, help="until")
    ap.add_argument("-t", "--threads", required=True, help="threads")
    args = vars(ap.parse_args())
    start_date = datetime.fromisoformat(args['since'])
    end_date = datetime.fromisoformat(args['until'])
    delta = end_date - start_date

    with concurrent.futures.ThreadPoolExecutor(max_workers=int(args['threads'])) as executor:
        futures = []
        for i in range(delta.days + 1):
            date_init = (start_date + timedelta(days=i)).isoformat()
            date_end = (start_date + timedelta(days=i + 1)).isoformat()
            futures.append(
                executor.submit(worker_twint, query=args['query'], date_init=date_init, date_end=date_end,
                                method=eval(args['method'])))
            futures.append(
                executor.submit(worker_snscrape, query=args['query'], date_init=date_init, date_end=date_end,
                                method=eval(args['method'])))
            futures.append(
                executor.submit(worker_tweepy, query=args['query'], date_init=date_init, date_end=date_end,
                                method=eval(args['method'])))
            futures.append(
                executor.submit(worker_GetOldTweets3, query=args['query'], date_init=date_init, date_end=date_end,
                                method=eval(args['method'])))