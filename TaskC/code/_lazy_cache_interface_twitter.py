#
# Willie Boag
#
# keeping this local to C (avoid shared resource headaches)
#



import os
import sys
import pickle
import urllib2

from twitter import oauth_dance, read_token_file, Twitter, OAuth, TwitterError
import twitter.api
import datetime
import time


# TODO - lookup real maximum
maxTweets = 20000


class Cache:

    def __init__(self):
        self.filename = os.path.join(os.getenv('BISCUIT_DIR'),'TaskC/etc/cache')
        self.loaded = {}
        self.new = {}
        '''
        print '\tcache constructor (%s)' % os.path.basename(self.filename)

        # Old lookups
        try:
            self.cache = pickle.load( open( self.filename ,"rb" ) )
        except IOError:
            self.cache = {}

        # New lookups
        self.new = {}
        '''


    def make_key(self, *args, **kwargs):
        # Query keyword and count determine which file to load
        key = ''

        if 'q' in kwargs:
            key += kwargs['q'].replace(' ','_')
        else:
            key += 'no_q'

        if 'count' in kwargs:
            key += str(kwargs['count'])
        else:
            key += 'no_count'

        return key


    def has_key(self, *args, **kwargs):
        key = self.make_key(*args, **kwargs)
        return key in self.loaded


    def add_value(self, key, value):
        print 'adding new value'


    def get_value(self, *args, **kwargs):
        # Get from cache (load if necesarry)
        key = self.make_key(*args, **kwargs)
        pass

    def __del__(self):
        '''
        import os, pickle
        print '\tcache destructor (%s)' % os.path.basename(self.filename)

        # Only re-pickle object if there's anything new to pickle
        if len(self.new):
            #print 'dumping'
            total = self.cache
            total.update(self.new)
            pickle.dump(total, open(self.filename,"wb"))
        '''


# Instantiate cache
cache = Cache()


class TwitterInterface(Twitter):

    def __init__(self, connect=True):

        # Offline?
        if connect:
            # Twitter credentials
            CONSUMER_KEY='JEdRRoDsfwzCtupkir4ivQ'
            CONSUMER_SECRET='PAbSSmzQxbcnkYYH2vQpKVSq2yPARfKm0Yl6DrLc'

            MY_TWITTER_CREDS = os.path.expanduser('~/.my_app_credentials')
            if not os.path.exists(MY_TWITTER_CREDS):
                oauth_dance("Semeval sentiment analysis", CONSUMER_KEY, CONSUMER_SECRET, MY_TWITTER_CREDS)
            oauth_token, oauth_secret = read_token_file(MY_TWITTER_CREDS)
            self.t = Twitter(auth=OAuth(oauth_token, oauth_secret, CONSUMER_KEY, CONSUMER_SECRET))


    #@memoize
    def search_tweets(self, *args, **kwargs):

        # Is answer cached?
        if cache.has_key(*args, **kwargs):
            print 'YES'
        else:
            print 'NO'
        exit()

        try:
            return self.t.search.tweets(*args, **kwargs)
        except TwitterError as e:
            if e.e.code == 429:
                rate = self.t.application.rate_limit_status()
                reset = rate['resources']['statuses']['/statuses/show/:id']['reset']
                now = datetime.datetime.today()
                future = datetime.datetime.fromtimestamp(reset)
                seconds = (future-now).seconds+1
                if seconds < 10000:
                    sys.stderr.write("Rate limit exceeded, sleeping for %s seconds until %s\n" % (seconds, future))
                    time.sleep(seconds)
            try:
                return self.t.search.tweets(*args, **kwargs)
            except TwitterError as e:
                sys.stderr.write("Still didn't work. Giving up.")
                return None
                

    def __del__(self):
        cache.__del__()
