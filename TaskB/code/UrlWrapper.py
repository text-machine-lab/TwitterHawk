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

from cache import Cache



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



# Create UrlCache object
cache = Cache('url')



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
