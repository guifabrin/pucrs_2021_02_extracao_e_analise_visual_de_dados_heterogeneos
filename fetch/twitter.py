import snscrape.modules.twitter as sntwitter


def fetch(query, date_init, date_end, store_method):
    print(query + ' since:' + date_init + ' until:' + date_end)

    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(
            query + ' since:' + date_init + ' until:' + date_end).get_items()):
        store_method(tweet)
