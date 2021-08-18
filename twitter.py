import tweepy
import json
import os

auth = tweepy.OAuthHandler('46pvnSwIVylfWepbPsP4433wL', 'xWDPHaUkk0ub93qj1DaYgJcO8QtkPUhNFIE7uBAvzbSVLLpLzR')
auth.set_access_token('1952916806-9WbU9ROPLd4aVPprQZqWJhaW4RSXrBw4oK8A4Ow',
                      'gW5iuYPtrTxVhPmQxBemsKz6jCAOqbYx1fT0ewKHFyAkG')
api = tweepy.API(auth)
page = 0
done = []
user = 'elonmusk'
total_tweets = 16000
directory = './cache/twitter/' + user + '/'

if os.path.isfile(directory + '/done.json'):
    file = open(directory + '/done.json', )
    done = json.load(file)


def fetch_tweets(number_page):
    limit = 200
    tweets = api.user_timeline(screen_name=user, count=limit, tweet_mode='extended', page=page)
    if not os.path.exists(directory):
        os.makedirs(directory)
    for tweet in tweets:
        filename = directory + tweet.created_at.strftime("%Y%m%d%H%M%S") + '.json'
        if os.path.isfile(filename):
            print('Tweet', tweet.created_at, 'already recovered')
            continue
        with open(filename, 'w') as outfile:
            json.dump(tweet._json, outfile)
    if len(tweets) != limit:
        print('Limit does not matching on page', page, 're trying')
        return fetch_tweets(number_page)
    print('Ended', number_page)
    done.append(number_page)
    with open(directory + '/done.json', 'w') as outfile:
        json.dump(done, outfile)


while page < total_tweets / 200:
    page += 1
    if page in done:
        print('Page', page, 'already fetched')
        continue
    print('Starting', page)
    fetch_tweets(page)
