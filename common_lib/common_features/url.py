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


# Add common-lib code to system path
sources = os.getenv('BISCUIT_DIR')
if sources not in sys.path: sys.path.append(sources)

from common_lib.cache                      import Cache
from common_lib.common_features.utilities  import is_url, normalize_phrase_TaskB





class Url:


    def __init__(self):
        # Cache HTML data lookup (only load if necessary)
        self.html_cache = None

        # Cache url features
        self.features_cache = Cache('url')



    def get_title(self, url):

        # Check cache for title (parsing HTML takes time)
        key = 'url--' + url + '--title'
        if self.features_cache.has_key(key):
            return self.features_cache.get_map(key)

        # Manually parse HTML data
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
            print 'Exception (', url,  ') - ', e

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
        self.features_cache.add_map(key, title)

        return title



    def domain(self, url):

        # Check cache for title (parsing HTML takes time)
        key = 'url--' + url + '--domain'
        if self.features_cache.has_key(key):
            return self.features_cache.get_map(key)

        # resolve url basename
        url = self.resolve(url)[1]
        if url == 'http://cannotread':
            site = None
        else:

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
                    site = candidates[-1]
                else:
                    site = matches[-1]

            else:
                # Else: No '/' after the '.com'
                outer_regex = 'https?://([^/]+)'
                site = re.search(outer_regex, url).group(1)

        # Add title to cache
        #print 'adding: ', title
        self.features_cache.add_map(key, site)

        return site



    def features(self, url):

        feats = {}

        # Feature: URL Domain Name
        basename = self.domain(url)
        if basename:
            feats['url-domain'] = basename

        # Feature: Title
        title = self.get_title(url)
        if title:
            # Note: TaskB normalization because original indices don't matter
            toks = nltk.word_tokenize(title)
            normalized = normalize_phrase_TaskB(toks, stem=True)
            #print '\t', title
            #print '\t', normalized
            for word in normalized:
                feats[('url-title-unigram',word)] = 1

        #print '\nurl: ', url
        #print feats

        return feats



    def resolve(self, url):

        # Only load HTML data cache if necesarry (it's big & expensive)
        if self.html_cache == None:
            self.html_cache = Cache('html')

        # Normalize key
        url = url.strip(string.punctuation).strip()

        # Check cache for text
        if self.html_cache.has_key(url):

            #print 'READING CACHE!' +  ' ' + url

            # Cache lookup
            data, resolved = self.html_cache.get_map(url)

        else:

            #print 'NOT IN CACHE' +  ' ' + url

            # Establish connection
            try:
                uf = urllib2.urlopen(url)
            except Exception,e:
                val = ('', 'http://cannotread')
                self.html_cache.add_map(url, val)
                return val

            # Get HTML data
            try:
                data = uf.read()
            except Exception,e:
                print >>sys.stderr, '\tERROR: Could not read url ' + url
                data = ''

            # Get resolved url
            try:
                resolved = uf.geturl()
            except Exception,e:
                print >>sys.stderr, '\tERROR: Could not read url ' + url
                resolved = 'http://cannotread'

            # Save data in cache
            val = (data, resolved)
            self.html_cache.add_map(url, val)


        return data,resolved
