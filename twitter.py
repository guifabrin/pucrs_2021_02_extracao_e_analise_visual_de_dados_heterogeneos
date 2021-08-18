import tweepy
import json
import os
import threading

auth = tweepy.OAuthHandler('46pvnSwIVylfWepbPsP4433wL', 'xWDPHaUkk0ub93qj1DaYgJcO8QtkPUhNFIE7uBAvzbSVLLpLzR')

auth.set_access_token('1952916806-9WbU9ROPLd4aVPprQZqWJhaW4RSXrBw4oK8A4Ow',
                      'gW5iuYPtrTxVhPmQxBemsKz6jCAOqbYx1fT0ewKHFyAkG')

api = tweepy.API(auth)


def obter_tweets(user, limit=10, page=1):
    return api.user_timeline(screen_name=user, count=limit, tweet_mode='extended', page=page)


def th(page):
    tweets = obter_tweets(user=user, limit=200, page=page)
    directory = './cache/twitter/' + user + '/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    if len(tweets) != 200:
        return th(page)
    for tweet in tweets:
        filename = directory + tweet.created_at.strftime("%Y%m%d%H%M%S") + '.json'
        if os.path.isfile(filename):
            continue
        with open(filename, 'w') as outfile:
            json.dump(tweet._json, outfile)
    print('finalizado', page)


user = 'elonmusk'
page = 1
total = 16000
print(total/200)
while page < total/200:
    x = threading.Thread(target=th, args=(page,))
    x.start()
    page += page + 1
