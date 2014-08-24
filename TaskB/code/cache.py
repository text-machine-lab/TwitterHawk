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



BASE_DIR = os.path.join(os.getenv('BISCUIT_DIR'),'TaskB')



class Cache:
    def __init__(self, name):
        #print '\tcache constructor (%s)' % name
        self.filename = os.path.join(BASE_DIR, 'etc/%s_cache' % name)

        try:
            self.cache = pickle.load( open( self.filename ,"rb" ) )
        except IOError:
            self.cache = {}
        except Exception, e:
            print >>sys.stderr, 'Cache error - ' + name
            print >>sys.stderr, 'Exception: ', e
            self.cache = {}

    def has_key(self, key):
        return self.cache.has_key( str(key) )

    def add_map(self, key, value):
        self.cache[ str(key) ] = value

    def get_map(self, key):
        return self.cache[ str(key) ]

    def __del__(self):
        import os, pickle
        #print '\tcache destructor (%s)' % os.path.basename(self.filename)
        pickle.dump(self.cache, open(self.filename,"wb"))

