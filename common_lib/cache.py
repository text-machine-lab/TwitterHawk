#-------------------------------------------------------------------------------
# Name:        cache.py
#
# Purpose:     General purpose cache.
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import urllib2
import re
import os
import sys
import cPickle as pickle



BASE_DIR = '/data1/nlp-data/twitter-caches'



class Cache:
    def __init__(self, name):
        print '\tcache constructor (%s_cache)' % name
        self.filename = os.path.join(BASE_DIR, '%s_cache' % name)

        try:
            self.cache = pickle.load( open( self.filename ,"rb" ) )
        except IOError:
            self.cache = {}

        # Newly added mappings
        self.new = {}

    def has_key(self, key):
        skey = unicode(key)
        return self.cache.has_key(skey) or self.new.has_key(key)

    def add_map(self, key, value):
        skey = unicode(key)
        self.new[ skey ] = value

    def get_map(self, key):
        skey = unicode(key)
        if skey in self.new:   return   self.new[skey]
        if skey in self.cache: return self.cache[skey]
        raise KeyError(skey)

    def __del__(self):
        import os, pickle
        print '\tcache destructor (%s)' % os.path.basename(self.filename)

        # Only re-pickle object if there's anything new to pickle
        if len(self.new):
            total = self.cache
            total.update(self.new)
            pickle.dump(total, open(self.filename,"wb"))
