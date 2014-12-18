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

from read_config import enabled_modules


class Cache:
    def __init__(self, name):

        # Disable cache?
        base_dir = enabled_modules['caches']
        if not base_dir:
            self.enabled_cache = False
            self.cache = {}
            self.new = {}
            self.filename = ''
            return

        self.enabled_cache = True

        print '\tcache constructor (%s_cache)' % name
        self.filename = os.path.join(base_dir, '%s_cache' % name)
        #print self.filename

        try:
            self.cache = pickle.load( open( self.filename ,"rb" ) )
        except IOError:
            print 'IOError making cache'
            self.cache = {}

        # Newly added mappings
        self.new = {}

    def has_key(self, key):
        skey = key
        #skey = unicode(key.decode('utf-8'))
        return self.cache.has_key(skey) or self.new.has_key(key)

    def add_map(self, key, value):
        skey = key
        #skey = unicode(key.decode('utf-8'))
        self.new[ skey ] = value

    def get_map(self, key):
        skey = key
        #skey = unicode(key.decode('utf-8'))
        if skey in self.new:   return   self.new[skey]
        if skey in self.cache: return self.cache[skey]
        raise KeyError(skey)

    def __del__(self):
        if not self.enabled_cache: return

        import os
        print '\tcache destructor (%s)' % os.path.basename(self.filename)

        # Only re-pickle object if there's anything new to pickle
        import pickle
        if self.enabled_cache and len(self.new):
            total = self.cache
            total.update(self.new)
            pickle.dump(total, open(self.filename,"wb"))
