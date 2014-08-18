#-------------------------------------------------------------------------------
# Name:        UrlWrapper.py
#
# Purpose:     Get HTML from a given URL (and cache results)
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import urllib2
import re
import os
import sys
#import cPickle as pickle
import pickle


BASE_DIR = os.path.join(os.getenv('BISCUIT_DIR'),'TaskB')


# Mimic functionality of urllib
class MyUrl:
    def __init__(self, txt, url):
        self.txt = txt
        self.url = url

    def read(self):
        return self.txt

    def geturl(self):
        return self.url



# Cache queries
class UrlCache:
    def __init__(self):
        try:
            self.filename = os.path.join(BASE_DIR,'etc/url_cache')
            self.cache = pickle.load( open( self.filename ,"rb" ) )
        except IOError:
            self.cache = {}

    def has_key(self, key):
        return self.cache.has_key( str(key) )

    def add_map(self, key, value):
        self.cache[ str(key) ] = value

    def get_map(self, key):
        return self.cache[ str(key) ]

    def __del__(self):
        import pickle                                       # Not sure why, put the 'pickle' module gets set to None
        pickle.dump(self.cache, open(self.filename,"wb"))



# Create UrlCache object
cache = UrlCache()



def urlopen(url):


    # Check cache for text
    if cache.has_key(url):

        #print 'READING CACHE!' +  ' ' + url

        # Cache lookup
        data, resolved = cache.get_map(url)
        return MyUrl(data, resolved)

    else:

        #print 'NOT IN CACHE' +  ' ' + url

        # Establish connection
        try:
            uf = urllib2.urlopen(url)
        except Exception,e:
            val = ('Cannot read data from url', 'http://cannotread')
            cache.add_map(url, val)
            return MyUrl(val[0], val[1])

        # Get HTML data
        try:
            data = uf.read()
        except Exception,e:
            print >>sys.stderr, '\tERROR: Could not read url ' + url
            data = 'Cannot read data from url'

        # Get resolved url
        try:
            resolved = uf.geturl()
        except Exception,e:
            print >>sys.stderr, '\tERROR: Could not read url ' + url
            resolved = 'http://cannotread'

        # Save data in cache
        val = (data, resolved)
        cache.add_map(url, val)

        return MyUrl(data, resolved)
