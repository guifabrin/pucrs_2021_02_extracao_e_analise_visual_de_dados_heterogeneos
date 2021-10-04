import argparse
import os
from datetime import datetime
import MetaTrader5 as mt5
import time

from dotenv import dotenv_values

config = dotenv_values(".env")


class Arg:
    def __init__(self):
        self.count = 10000000
        self.frame = None
        self.favorite_multiplier = None
        self.retweets_multiplier = None
        self.database = 'mongodb'
        self.since = None
        self.until = None
        self.show = False
        if 'PATH_TO_SAVE' in config:
            self.path_img = config['PATH_TO_SAVE']

    @property
    def mt5_timeframe(self):
        return getattr(mt5, self.frame)

    @property
    def str_timeframe(self):
        return self.frame.split('_')[1]

    @property
    def panda_frequency(self):
        if self.str_timeframe[0] == 'M':
            if self.str_timeframe[1] == 'N':
                return 'M'
            return 'T'
        return self.str_timeframe[0]

    @property
    def str_since(self):
        return self.since.isoformat().split('T')[0]

    @property
    def str_until(self):
        return self.until.isoformat().split('T')[0]

    @property
    def subtitle(self):
        return '{} x twitter count about "{}" from {} to {} in \n timeframe {} with importance {} vs {}'.format(
            self.tick,
            self.query,
            self.str_since,
            self.str_until,
            self.str_timeframe,
            self.favorite_multiplier,
            self.retweets_multiplier
        )

    def filename(self, extra=''):
        directory = '{}\\{}_{}\\{}_{}\\{}\\{}_{}\\'.format(
            self.path_img,
            self.tick,
            self.query,
            self.str_since,
            self.str_until,
            self.str_timeframe,
            self.favorite_multiplier,
            self.retweets_multiplier)
        if not os.path.exists(directory):
            os.makedirs(directory)
        return '{}image{}'.format(
            directory,
            extra
        )


def parse():
    ap = argparse.ArgumentParser()

    ap.add_argument("-t", "--tick", required=True, help="tick to generate first part of the chart")
    ap.add_argument("-q", "--query", required=True, help="query to search into database")
    ap.add_argument("-s", "--since", required=True, help="since date")
    ap.add_argument("-u", "--until", required=True, help="until date")
    ap.add_argument("-f", "--frame", required=True, help="frame data from mt5 lib like TIMEFRAME_H1")

    ap.add_argument("-d", "--database", required=False, help="database to retrive data")
    ap.add_argument("-c", "--count", required=False, help="max ticks count")
    ap.add_argument("-m", "--favorite", required=False, help="favorite multiplier")
    ap.add_argument("-r", "--retweets", required=False, help="retweets multiplier")
    ap.add_argument("-p", "--path", required=False, help="path to save generated image")
    ap.add_argument("-x", "--show", required=False, help="show image")

    args = vars(ap.parse_args())
    arg = Arg()
    arg.tick = args['tick']
    arg.query = args['query']
    arg.since = datetime.strptime(args['since'], '%Y-%m-%d %H:%M:%S')
    arg.until = datetime.strptime(args['until'], '%Y-%m-%d %H:%M:%S')
    arg.frame = args['frame']

    if args['favorite']:
        arg.favorite_multiplier = int(args['favorite'])

    if args['retweets']:
        arg.retweets_multiplier = int(args['retweets'])

    if args['count']:
        arg.count = args['count']

    if args['path']:
        arg.path_img = args['path']

    if args['database']:
        arg.database = args['database']

    if args['show']:
        arg.show = bool(args['show'])

    return arg