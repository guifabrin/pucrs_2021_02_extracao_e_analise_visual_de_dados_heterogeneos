import datetime
import json
import logging
import random
import re
import time
import urllib.parse
import abc
import logging
import time

import requests
import bs4

import argparse
import contextlib
import datetime
import inspect
import logging
# Imported in parse_args() after setting up the logger:
# import snscrape.base
# import snscrape.modules
# import snscrape.version
import tempfile

import requests.models

## Logging
dumpLocals = False
logger = logging  # Replaced below after setting the logger class


class Logger(logging.Logger):
    def _log_with_stack(self, level, *args, **kwargs):
        super().log(level, *args, **kwargs)
        if dumpLocals:
            stack = inspect.stack()
            if len(stack) >= 3:
                name = _dump_stack_and_locals(stack[2:][::-1])
                super().log(level, f'Dumped stack and locals to {name}')

    def warning(self, *args, **kwargs):
        self._log_with_stack(logging.WARNING, *args, **kwargs)

    def error(self, *args, **kwargs):
        self._log_with_stack(logging.ERROR, *args, **kwargs)

    def critical(self, *args, **kwargs):
        self._log_with_stack(logging.CRITICAL, *args, **kwargs)

    def log(self, level, *args, **kwargs):
        if level >= logging.WARNING:
            self._log_with_stack(level, *args, **kwargs)
        else:
            super().log(level, *args, **kwargs)


def _requests_preparedrequest_repr(name, request):
    ret = []
    ret.append(repr(request))
    ret.append(f'\n  {name}.method = {request.method}')
    ret.append(f'\n  {name}.url = {request.url}')
    ret.append(f'\n  {name}.headers = \\')
    for field in request.headers:
        ret.append(f'\n    {field} = {_repr("_", request.headers[field])}')
    if request.body:
        ret.append(f'\n  {name}.body = ')
        ret.append(_repr('_', request.body).replace('\n', '\n  '))
    return ''.join(ret)


def _requests_response_repr(name, response, withHistory=True):
    ret = []
    ret.append(repr(response))
    ret.append(f'\n  {name}.url = {response.url}')
    ret.append(f'\n  {name}.request = ')
    ret.append(_repr('_', response.request).replace('\n', '\n  '))
    if withHistory and response.history:
        ret.append(f'\n  {name}.history = [')
        for previousResponse in response.history:
            ret.append(f'\n    ')
            ret.append(_requests_response_repr('_', previousResponse, withHistory=False).replace('\n', '\n    '))
        ret.append('\n  ]')
    ret.append(f'\n  {name}.status_code = {response.status_code}')
    ret.append(f'\n  {name}.headers = \\')
    for field in response.headers:
        ret.append(f'\n    {field} = {_repr("_", response.headers[field])}')
    ret.append(f'\n  {name}.content = {_repr("_", response.content)}')
    return ''.join(ret)


def _repr(name, value):
    if type(value) is requests.models.Response:
        return _requests_response_repr(name, value)
    if type(value) is requests.models.PreparedRequest:
        return _requests_preparedrequest_repr(name, value)
    valueRepr = repr(value)
    if '\n' in valueRepr:
        return ''.join(['\\\n  ', valueRepr.replace('\n', '\n  ')])
    return valueRepr


@contextlib.contextmanager
def _dump_locals_on_exception():
    try:
        yield
    except Exception as e:
        trace = inspect.trace()
        if len(trace) >= 2:
            name = _dump_stack_and_locals(trace[1:], exc=e)
            logger.fatal(f'Dumped stack and locals to {name}')
        raise


def _dump_stack_and_locals(trace, exc=None):
    with tempfile.NamedTemporaryFile('w', prefix='snscrape_locals_', delete=False) as fp:
        if exc is not None:
            fp.write('Exception:\n')
            fp.write(f'  {type(exc).__module__}.{type(exc).__name__}: {exc!s}\n')
            fp.write(f'  args: {exc.args!r}\n')
            fp.write('\n')

        fp.write('Stack:\n')
        for frameRecord in trace:
            fp.write(f'  File "{frameRecord.filename}", line {frameRecord.lineno}, in {frameRecord.function}\n')
            for line in frameRecord.code_context:
                fp.write(f'    {line.strip()}\n')
        fp.write('\n')

        for frameRecord in trace:
            module = inspect.getmodule(frameRecord[0])
            if not module.__name__.startswith('snscrape.') and module.__name__ != 'snscrape':
                continue
            locals_ = frameRecord[0].f_locals
            fp.write(
                f'Locals from file "{frameRecord.filename}", line {frameRecord.lineno}, in {frameRecord.function}:\n')
            for variableName in locals_:
                variable = locals_[variableName]
                varRepr = _repr(variableName, variable)
                fp.write(f'  {variableName} {type(variable)} = ')
                fp.write(varRepr.replace('\n', '\n  '))
                fp.write('\n')
            fp.write('\n')
            if 'self' in locals_ and hasattr(locals_['self'], '__dict__'):
                fp.write(f'Object dict:\n')
                fp.write(repr(locals_['self'].__dict__))
                fp.write('\n\n')
        name = fp.name
    return name


def parse_datetime_arg(arg):
    for format in ('%Y-%m-%d %H:%M:%S %z', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %z', '%Y-%m-%d'):
        try:
            d = datetime.datetime.strptime(arg, format)
        except ValueError:
            continue
        else:
            if d.tzinfo is None:
                return d.replace(tzinfo=datetime.timezone.utc)
            return d
    # Try treating it as a unix timestamp
    try:
        d = datetime.datetime.fromtimestamp(int(arg), datetime.timezone.utc)
    except ValueError:
        pass
    else:
        return d
    raise argparse.ArgumentTypeError(f'Cannot parse {arg!r} into a datetime object')


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', '--verbosity', dest='verbosity', action='count', default=0,
                        help='Increase output verbosity')
    parser.add_argument('--dump-locals', dest='dumpLocals', action='store_true', default=False,
                        help='Dump local variables on serious log messages (warnings or higher)')
    parser.add_argument('--retry', '--retries', dest='retries', type=int, default=3, metavar='N',
                        help='When the connection fails or the server returns an unexpected response, retry up to N times with an exponential backoff')
    parser.add_argument('-n', '--max-results', dest='maxResults', type=int, metavar='N',
                        help='Only return the first N results')
    parser.add_argument('-f', '--format', dest='format', type=str, default=None, help='Output format')
    parser.add_argument('--since', type=parse_datetime_arg, metavar='DATETIME',
                        help='Only return results newer than DATETIME')

    subparsers = parser.add_subparsers(dest='scraper', help='The scraper you want to use')
    classes = Scraper.__subclasses__()
    for cls in classes:
        if cls.name is not None:
            subparser = subparsers.add_parser(cls.name, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
            cls.setup_parser(subparser)
            subparser.set_defaults(cls=cls)
        classes.extend(cls.__subclasses__())

    args = parser.parse_args()

    # http://bugs.python.org/issue16308 / https://bugs.python.org/issue26510 (fixed in Python 3.7)
    if not args.scraper:
        raise RuntimeError('Error: no scraper specified')

    return args


def setup_logging():
    logging.setLoggerClass(Logger)
    global logger
    logger = logging.getLogger(__name__)


def configure_logging(verbosity, dumpLocals_):
    global dumpLocals
    dumpLocals = dumpLocals_

    rootLogger = logging.getLogger()

    # Set level
    if verbosity > 0:
        level = logging.INFO if verbosity == 1 else logging.DEBUG
        rootLogger.setLevel(level)
        for handler in rootLogger.handlers:
            handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter('{asctime}.{msecs:03.0f}  {levelname}  {name}  {message}',
                                  datefmt='%Y-%m-%d %H:%M:%S', style='{')

    # Remove existing handlers
    for handler in rootLogger.handlers:
        rootLogger.removeHandler(handler)

    # Add stream handler
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    rootLogger.addHandler(handler)


def main():
    setup_logging()
    args = parse_args()
    configure_logging(args.verbosity, args.dumpLocals)
    scraper = args.cls.from_args(args)

    i = 0
    with _dump_locals_on_exception():
        for i, item in enumerate(scraper.get_items(), start=1):
            if args.since is not None and item.date < args.since:
                logger.info(f'Exiting due to reaching older results than {args.since}')
                break
            if args.format is not None:
                print(args.format.format(**item._asdict()))
            else:
                print(item)
            if args.maxResults and i >= args.maxResults:
                logger.info(f'Exiting after {i} results')
                break
        else:
            logger.info(f'Done, found {i} results')


logger = logging.getLogger(__name__)


class Item:
    '''An abstract base class for an item returned by the scraper's get_items generator.

    An item can really be anything. The string representation should be useful for the CLI output (e.g. a direct URL for the item).'''

    @abc.abstractmethod
    def __str__(self):
        pass


class URLItem(Item):
    '''A generic item which only holds a URL string.'''

    def __init__(self, url):
        self._url = url

    @property
    def url(self):
        return self._url

    def __str__(self):
        return self._url


class ScraperException(Exception):
    pass


class Scraper:
    '''An abstract base class for a scraper.'''

    name = None

    def __init__(self, retries=3):
        self._retries = retries
        self._session = requests.Session()

    @abc.abstractmethod
    def get_items(self):
        '''Iterator yielding Items.'''
        pass

    def _request(self, method, url, params=None, data=None, headers=None, timeout=10, responseOkCallback=None):
        for attempt in range(self._retries + 1):
            # The request is newly prepared on each retry because of potential cookie updates.
            req = self._session.prepare_request(
                requests.Request(method, url, params=params, data=data, headers=headers))
            logger.info(f'Retrieving {req.url}')
            logger.debug(f'... with headers: {headers!r}')
            if data:
                logger.debug(f'... with data: {data!r}')
            try:
                r = self._session.send(req, timeout=timeout)
            except requests.exceptions.RequestException as exc:
                if attempt < self._retries:
                    retrying = ', retrying'
                    level = logging.WARNING
                else:
                    retrying = ''
                    level = logging.ERROR
                logger.log(level, f'Error retrieving {req.url}: {exc!r}{retrying}')
            else:
                if responseOkCallback is not None:
                    success, msg = responseOkCallback(r)
                else:
                    success, msg = (True, None)
                msg = f': {msg}' if msg else ''

                if success:
                    logger.debug(f'{req.url} retrieved successfully{msg}')
                    return r
                else:
                    if attempt < self._retries:
                        retrying = ', retrying'
                        level = logging.WARNING
                    else:
                        retrying = ''
                        level = logging.ERROR
                    logger.log(level, f'Error retrieving {req.url}{msg}{retrying}')
            if attempt < self._retries:
                sleepTime = 1.0 * 2 ** attempt  # exponential backoff: sleep 1 second after first attempt, 2 after second, 4 after third, etc.
                logger.info(f'Waiting {sleepTime:.0f} seconds')
                time.sleep(sleepTime)
        else:
            msg = f'{self._retries + 1} requests to {req.url} failed, giving up.'
            logger.fatal(msg)
            raise ScraperException(msg)
        raise RuntimeError('Reached unreachable code')

    def _get(self, *args, **kwargs):
        return self._request('GET', *args, **kwargs)

    def _post(self, *args, **kwargs):
        return self._request('POST', *args, **kwargs)

    @classmethod
    @abc.abstractmethod
    def setup_parser(cls, subparser):
        pass

    @classmethod
    @abc.abstractmethod
    def from_args(cls, args):
        pass

logger = logging.getLogger(__name__)


class Tweet(Item):
    def __init__(self, url, date, content, tweetID, username, outlinks, outlinkss, tcooutlinks, tcooutlinkss, user_id,
                 favorite_count, retweet_count):
        self.url = url
        self.date = date
        self.content = content
        self.tweetID = tweetID
        self.username = username
        self.outlinks = outlinks
        self.outlinkss = outlinkss
        self.tcooutlinks = tcooutlinks
        self.tcooutlinkss = tcooutlinkss
        self.user_id = user_id
        self.favorite_count = favorite_count
        self.retweet_count = retweet_count

    def __str__(self):
        return self.url


class Account(Item):
    def __init__(self, username):
        self.username = username

    @property
    def url(self):
        return f'https://twitter.com/{self.username}'

    def __str__(self):
        return self.url


class TwitterCommonScraper(Scraper):
    def _feed_to_items(self, feed):
        for tweet in feed:
            username = tweet.find('span', 'username').find('b').text
            tweetID = tweet['data-item-id']
            url = f'https://twitter.com/{username}/status/{tweetID}'

            date = None
            timestampA = tweet.find('a', 'tweet-timestamp')
            if timestampA:
                timestampSpan = timestampA.find('span', '_timestamp')
                if timestampSpan and timestampSpan.has_attr('data-time'):
                    date = datetime.datetime.fromtimestamp(int(timestampSpan['data-time']), datetime.timezone.utc)
            if not date:
                logger.warning(f'Failed to extract date for {url}')

            contentP = tweet.find('p', 'tweet-text')
            content = None
            outlinks = []
            tcooutlinks = []
            if contentP:
                content = contentP.text
                for a in contentP.find_all('a'):
                    if a.has_attr('href') and not a['href'].startswith('/') and (
                            not a.has_attr('class') or 'u-hidden' not in a['class']):
                        if a.has_attr('data-expanded-url'):
                            outlinks.append(a['data-expanded-url'])
                        else:
                            logger.warning(f'Ignoring link without expanded URL on {url}: {a["href"]}')
                        tcooutlinks.append(a['href'])
            else:
                logger.warning(f'Failed to extract content for {url}')
            card = tweet.find('div', 'card2')
            if card and 'has-autoplayable-media' not in card['class']:
                for div in card.find_all('div'):
                    if div.has_attr('data-card-url'):
                        outlinks.append(div['data-card-url'])
                        tcooutlinks.append(div['data-card-url'])
            outlinks = list(dict.fromkeys(
                outlinks))  # Deduplicate in case the same link was shared more than once within this tweet; may change order on Python 3.6 or older
            tcooutlinks = list(dict.fromkeys(tcooutlinks))
            yield Tweet(url, date, content, tweetID, username, outlinks, ' '.join(outlinks), tcooutlinks,
                        ' '.join(tcooutlinks))

    def _check_json_callback(self, r):
        if r.headers.get('content-type') != 'application/json;charset=utf-8':
            return False, f'content type is not JSON'
        return True, None


class TwitterSearchScraper(TwitterCommonScraper):
    name = 'twitter-search'

    def __init__(self, query, cursor=None, **kwargs):
        super().__init__(**kwargs)
        self._query = query
        self._cursor = cursor
        self._userAgent = f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.{random.randint(0, 9999)} Safari/537.{random.randint(0, 99)}'
        self._baseUrl = 'https://twitter.com/search?' + urllib.parse.urlencode(
            {'f': 'live', 'lang': 'en', 'q': self._query, 'src': 'spelling_expansion_revert_click'})

    def _get_guest_token(self):
        logger.info(f'Retrieving guest token from search page')
        r = self._get(self._baseUrl, headers={'User-Agent': self._userAgent})
        match = re.search(
            r'document\.cookie = decodeURIComponent\("gt=(\d+); Max-Age=10800; Domain=\.twitter\.com; Path=/; Secure"\);',
            r.text)
        if match:
            logger.debug('Found guest token in HTML')
            return match.group(1)
        if 'gt' in r.cookies:
            logger.debug('Found guest token in cookies')
            return r.cookies['gt']
        raise ScraperException('Unable to find guest token')

    def _check_scroll_response(self, r):
        if r.status_code == 429:
            # Accept a 429 response as "valid" to prevent retries; handled explicitly in get_items
            return True, None
        if r.headers.get('content-type') != 'application/json;charset=utf-8':
            return False, f'content type is not JSON'
        if r.status_code != 200:
            return False, f'non-200 status code'
        return True, None

    def get_items(self):
        headers = {
            'User-Agent': self._userAgent,
            'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'Referer': self._baseUrl,
        }
        guestToken = None
        cursor = self._cursor
        while True:
            if not guestToken:
                guestToken = self._get_guest_token()
                self._session.cookies.set('gt', guestToken, domain='.twitter.com', path='/', secure=True,
                                          expires=time.time() + 10800)
                headers['x-guest-token'] = guestToken

            logger.info(f'Retrieving scroll page {cursor}')
            params = {
                'include_profile_interstitial_type': '1',
                'include_blocking': '1',
                'include_blocked_by': '1',
                'include_followed_by': '1',
                'include_want_retweets': '1',
                'include_mute_edge': '1',
                'include_can_dm': '1',
                'include_can_media_tag': '1',
                'skip_status': '1',
                'cards_platform': 'Web-12',
                'include_cards': '1',
                'include_composer_source': 'true',
                'include_ext_alt_text': 'true',
                'include_reply_count': '1',
                'tweet_mode': 'extended',
                'include_entities': 'true',
                'include_user_entities': 'true',
                'include_ext_media_color': 'true',
                'include_ext_media_availability': 'true',
                'send_error_codes': 'true',
                'simple_quoted_tweets': 'true',
                'q': self._query,
                'tweet_search_mode': 'live',
                'count': '100',
                'query_source': 'spelling_expansion_revert_click',
            }
            if cursor:
                params['cursor'] = cursor
            params['pc'] = '1'
            params['spelling_corrections'] = '1'
            params['ext'] = 'mediaStats%2CcameraMoment'
            r = self._get('https://api.twitter.com/2/search/adaptive.json', params=params, headers=headers,
                          responseOkCallback=self._check_scroll_response)
            if r.status_code == 429:
                guestToken = None
                del self._session.cookies['gt']
                del headers['x-guest-token']
                continue
            try:
                obj = r.json()
            except json.JSONDecodeError as e:
                raise ScraperException('Received invalid JSON from Twitter') from e

            # No data format test, just a hard and loud crash if anything's wrong :-)
            newCursor = None
            for instruction in obj['timeline']['instructions']:
                if 'addEntries' in instruction:
                    entries = instruction['addEntries']['entries']
                elif 'replaceEntry' in instruction:
                    entries = [instruction['replaceEntry']['entry']]
                else:
                    continue
                for entry in entries:
                    if entry['entryId'].startswith('sq-I-t-'):
                        if 'tweet' in entry['content']['item']['content']:
                            tweet = obj['globalObjects']['tweets'][entry['content']['item']['content']['tweet']['id']]
                        elif 'tombstone' in entry['content']['item']['content'] and 'tweet' in \
                                entry['content']['item']['content']['tombstone']:
                            tweet = obj['globalObjects']['tweets'][
                                entry['content']['item']['content']['tombstone']['tweet']['id']]
                        else:
                            raise ScraperException(f'Unable to handle entry {entry["entryId"]!r}')
                        tweetID = tweet['id']
                        content = tweet['full_text']
                        username = obj['globalObjects']['users'][tweet['user_id_str']]['screen_name']
                        date = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y').replace(
                            tzinfo=datetime.timezone.utc)
                        outlinks = [u['expanded_url'] for u in tweet['entities']['urls']]
                        tcooutlinks = [u['url'] for u in tweet['entities']['urls']]
                        url = f'https://twitter.com/{username}/status/{tweetID}'
                        yield Tweet(url, date, content, tweetID, username, outlinks, ' '.join(outlinks), tcooutlinks,
                                    ' '.join(tcooutlinks), tweet['user_id_str'], tweet['favorite_count'],
                                    tweet['retweet_count'])
                    elif entry['entryId'] == 'sq-cursor-bottom':
                        newCursor = entry['content']['operation']['cursor']['value']
            if not newCursor or newCursor == cursor:
                # End of pagination
                break
            cursor = newCursor

    @classmethod
    def setup_parser(cls, subparser):
        subparser.add_argument('--cursor', metavar='CURSOR')
        subparser.add_argument('query', help='A Twitter search string')

    @classmethod
    def from_args(cls, args):
        return cls(args.query, cursor=args.cursor, retries=args.retries)


class TwitterUserScraper(TwitterSearchScraper):
    name = 'twitter-user'

    def __init__(self, username, **kwargs):
        super().__init__(f'from:{username}', **kwargs)
        self._username = username

    @classmethod
    def setup_parser(cls, subparser):
        subparser.add_argument('username', help='A Twitter username (without @)')

    @classmethod
    def from_args(cls, args):
        return cls(args.username, retries=args.retries)


class TwitterHashtagScraper(TwitterSearchScraper):
    name = 'twitter-hashtag'

    def __init__(self, hashtag, **kwargs):
        super().__init__(f'#{hashtag}', **kwargs)
        self._hashtag = hashtag

    @classmethod
    def setup_parser(cls, subparser):
        subparser.add_argument('hashtag', help='A Twitter hashtag (without #)')

    @classmethod
    def from_args(cls, args):
        return cls(args.hashtag, retries=args.retries)


class TwitterThreadScraper(TwitterCommonScraper):
    name = 'twitter-thread'

    def __init__(self, tweetID=None, **kwargs):
        if tweetID is not None and tweetID.strip('0123456789') != '':
            raise ValueError('Invalid tweet ID, must be numeric')
        super().__init__(**kwargs)
        self._tweetID = tweetID

    def get_items(self):
        headers = {'User-Agent': f'Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.18'}

        # Fetch the page of the last tweet in the thread
        r = self._get(f'https://twitter.com/user/status/{self._tweetID}', headers=headers)
        soup = bs4.BeautifulSoup(r.text, 'lxml')

        # Extract tweets on that page in the correct order; first, the tweet that was supplied, then the ancestors with pagination if necessary
        tweet = soup.find('div', 'ThreadedConversation--permalinkTweetWithAncestors')
        if tweet:
            tweet = tweet.find('div', 'tweet')
        if not tweet:
            logger.warning('Tweet does not exist, is not a thread, or does not have ancestors')
            return
        items = list(self._feed_to_items([tweet]))
        assert len(items) == 1
        yield items[0]
        username = items[0].username

        ancestors = soup.find('div', 'ThreadedConversation--ancestors')
        if not ancestors:
            logger.warning('Tweet does not have ancestors despite claiming to')
            return
        feed = reversed(ancestors.find_all('li', 'js-stream-item'))
        yield from self._feed_to_items(feed)

        # If necessary, iterate through pagination until reaching the initial tweet
        streamContainer = ancestors.find('div', 'stream-container')
        if not streamContainer.has_attr('data-max-position') or streamContainer['data-max-position'] == '':
            return
        minPosition = streamContainer['data-max-position']
        while True:
            r = self._get(
                f'https://twitter.com/i/{username}/conversation/{self._tweetID}?include_available_features=1&include_entities=1&min_position={minPosition}',
                headers=headers,
                responseOkCallback=self._check_json_callback
            )

            obj = json.loads(r.text)
            soup = bs4.BeautifulSoup(obj['items_html'], 'lxml')
            feed = reversed(soup.find_all('li', 'js-stream-item'))
            yield from self._feed_to_items(feed)
            if not obj['has_more_items']:
                break
            minPosition = obj['max_position']

    @classmethod
    def setup_parser(cls, subparser):
        subparser.add_argument('tweetID', help='A tweet ID of the last tweet in a thread')

    @classmethod
    def from_args(cls, args):
        return cls(tweetID=args.tweetID, retries=args.retries)


class TwitterListPostsScraper(TwitterSearchScraper):
    name = 'twitter-list-posts'

    def __init__(self, listName, **kwargs):
        super().__init__(f'list:{listName}', **kwargs)
        self._listName = listName

    @classmethod
    def setup_parser(cls, subparser):
        subparser.add_argument('list', help='A Twitter list, formatted as "username/listname"')

    @classmethod
    def from_args(cls, args):
        return cls(args.list, retries=args.retries)


class TwitterListMembersScraper(TwitterCommonScraper):
    name = 'twitter-list-members'

    def __init__(self, listName, **kwargs):
        super().__init__(**kwargs)
        self._user, self._list = listName.split('/')

    def get_items(self):
        headers = {'User-Agent': f'Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.18'}

        baseUrl = f'https://twitter.com/{self._user}/lists/{self._list}/members'
        r = self._get(baseUrl, headers=headers)
        if r.status_code != 200:
            logger.warning('List not found')
            return
        soup = bs4.BeautifulSoup(r.text, 'lxml')
        container = soup.find('div', 'stream-container')
        if not container:
            raise ScraperException('Unable to find container')
        items = container.find_all('li', 'js-stream-item')
        if not items:
            logger.warning('Empty list')
            return
        for item in items:
            yield Account(username=item.find('div', 'account')['data-screen-name'])

        if not container.has_attr('data-min-position') or container['data-min-position'] == '':
            return
        maxPosition = container['data-min-position']
        while True:
            r = self._get(
                f'{baseUrl}/timeline?include_available_features=1&include_entities=1&max_position={maxPosition}&reset_error_state=false',
                headers=headers,
                responseOkCallback=self._check_json_callback
            )
            obj = json.loads(r.text)
            soup = bs4.BeautifulSoup(obj['items_html'], 'lxml')
            items = soup.find_all('li', 'js-stream-item')
            for item in items:
                yield Account(username=item.find('div', 'account')['data-screen-name'])
            if not obj['has_more_items']:
                break
            maxPosition = obj['min_position']

    @classmethod
    def setup_parser(cls, subparser):
        subparser.add_argument('list', help='A Twitter list, formatted as "username/listname"')

    @classmethod
    def from_args(cls, args):
        return cls(args.list, retries=args.retries)
