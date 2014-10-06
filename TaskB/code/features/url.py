#-------------------------------------------------------------------------------
# Name:        url.py
#
# Purpose:     Follow URLs from tweets and generate features.
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import os,sys
import nltk
import string
import re

import urllib2
from HTMLParser import HTMLParser
from BeautifulSoup import BeautifulSoup

from read_config import enabled_modules 
from cache       import Cache
from utilities   import is_url
import features  



BASE_DIR = os.path.join(os.getenv('BISCUIT_DIR'),'TaskB')



class Url:


    def __init__(self, feat_obj, data):

        # Cache HTML data lookup
        self.cache = Cache('url')

        # Used for avoiding infinite recursion if url title contains same url
        self.seen = {}

        # Retrieve all URLs
        # TODO - Follow all urls in order to find url closure
        urls   = [ w for t in data for w in t.split()   if is_url(w) ]
        titles = []
        for url in urls:
            title = self.get_title(url)
            if title:
                titles.append(title)

        # Run tagger on all URLs upfront (rather than individually)
        self.feat_obj = feat_obj
        if enabled_modules['twitter_nlp']:
            self.feat_obj.twitter_nlp.update(titles)



    def get_title(self, url):

        # Check cache for title (parsing HTML takes time)
        key = url + '--title'
        #if self.cache.has_key(key):
        #    return self.cache.get_map(key)

        try:
            # Get HTML data and url basename
            data,resolved = self.resolve(url)

            # Parse HTML
            data = data.decode('ascii','ignore')
            soup = BeautifulSoup(data)

            # Get title from HTML
            if soup.title:
                st = nltk.stem.PorterStemmer()
                h = HTMLParser()
                header = h.unescape( soup.title.getText(' ') )
                header = header.decode('ascii','ignore')
            else:
                header = ''

        except Exception,e:
            header = ''
            #print 'Exception (', url,  ') - ', e


        # Heuristic to trim domain name from title
        header = header.replace('\n',' ')
        title = header
        delims = ['\\|', '-']
        for d in delims:
            regex = '([^%s]+) %s .+' % (d,d)
            match = re.search(regex, header)
            if match:
                title = match.group(1)
                break


        # Add title to cache
        #print 'adding: ', title
        self.cache.add_map(key, title)

        return title



    def domain(self, url):

        not_domains = ['www', 'com']

        # Find all domain-name candidates
        outer_regex = 'https?://([^/]+)/'
        outer = re.search(outer_regex, url)
        if outer:

            # Get list of candidates (ex. ['www', 'facebook']
            outer = outer.group(1)
            inner_regex = '([^\.]+)\.'
            matches = re.findall(inner_regex, outer)

            # Filter out candidates that are definitely not domains
            matches = [ m for m in matches if  (m not in not_domains) ]

            # Pick best candidate
            # Heuristic: Rightmost candidate of length >= 3
            candidates = [ m for m in matches if len(m) >= 3 ]
            if candidates:
                return candidates[-1]
            else:
                return matches[-1]

        # Else: No '/' after the '.com'
        outer_regex = 'https?://([^/]+)'
        outer = re.search(outer_regex, url).group(1)
        return outer



    def features(self, url):

        features = {}

        # Avoid infininte recursion
        if url in self.seen:
            return self.seen[url]
        else:
            self.seen[url] = {}

        # Get HTML data and url basename
        data,resolved = self.resolve(url)


        # Feature: URL basename
        if resolved != 'http://cannotread':
            features['url-basename'] = self.domain(resolved)


        #print '\n\n'
        #print '\t', resolved


        # Feature: Title
        title = self.get_title(url)
        if title:
            # Run twitter_nlp
            pass
            #print title


        # Memoize
        self.seen[url] = features
        return features



    def resolve(self, url):

        url = url.strip(string.punctuation).strip()

        # Check cache for text
        if self.cache.has_key(url):

            #print 'READING CACHE!' +  ' ' + url

            # Cache lookup
            data, resolved = self.cache.get_map(url)

        else:

            print 'NOT IN CACHE' +  ' ' + url

            # Establish connection
            try:
                uf = urllib2.urlopen(url)
            except Exception,e:
                val = ('Cannot read data from url', 'http://cannotread')
                self.cache.add_map(url, val)
                return val

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
            self.cache.add_map(url, val)



        return data,resolved
