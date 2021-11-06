import argparse
import json
import os
from datetime import datetime

import MetaTrader5 as mt5

from src.helper import load_config

config = load_config()

class Arg:
    def __init__(self):
        self.count = 10000000
        self.frame = None
        self.database = 'mongodb'
        self.since = None
        self.until = None
        self.show = False
        self.tick = None
        self.query = None
        self.lines = {}
        self.ignore = False

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
        return '{} x twitter count about "{}" from {} to {} in \n timeframe {}'.format(
            self.tick,
            self.query,
            self.str_since,
            self.str_until,
            self.str_timeframe
        )

    def filename(self, extra=''):
        directory = '{}\\{}_{}\\{}_{}\\{}\\'.format(
            self.path_img,
            self.tick,
            self.query,
            self.str_since,
            self.str_until,
            self.str_timeframe)
        if not os.path.exists(directory):
            os.makedirs(directory)
        return '{}plot{}'.format(
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
    ap.add_argument("-d", "--database", required=True, help="")

    ap.add_argument("-c", "--count", required=False, help="max ticks count")
    ap.add_argument("-m", "--favorite", required=False, help="favorite multiplier")
    ap.add_argument("-r", "--retweets", required=False, help="retweets multiplier")
    ap.add_argument("-p", "--path", required=False, help="path to save generated image")
    ap.add_argument("-x", "--show", required=False, help="show image")
    ap.add_argument("-l", "--lines", required=False, help="vertical lines")
    ap.add_argument("-j", "--json", required=False, help="vertical lines json file")
    ap.add_argument("-i", "--importances", required=False,
                    help="importance calc where {f} is favorite and {t} is retweet")

    args = vars(ap.parse_args())
    arg = Arg()
    arg.tick = args['tick']
    arg.query = args['query']
    arg.since = datetime.strptime(args['since'], '%Y-%m-%d %H:%M:%S')
    arg.until = datetime.strptime(args['until'], '%Y-%m-%d %H:%M:%S')
    arg.frame = args['frame']
    arg.database = args['database']
    arg.path_img = config['PATH_TO_SAVE']+"\\"+arg.database+"\\"

    if args['count']:
        arg.count = args['count']

    if args['path']:
        arg.path_img = args['path']

    if args['show']:
        arg.show = bool(args['show'])

    if args['lines']:
        arg.lines = json.loads(args['lines'])

    if args['json']:
        f = open(args['json'], )
        arg.lines = json.load(f)

    if args['importances']:
        arg.importances = args['importances'].split(';')

    return arg
