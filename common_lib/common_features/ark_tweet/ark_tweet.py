######################################################################
#  CliCon - ark_tweet.py                                             #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Interface for twitter_nlp tools.                         #
######################################################################


import argparse

import os,sys
from collections import defaultdict
import string

from HTMLParser import HTMLParser


# Add common-lib code to system path
back = os.path.dirname
sources = back(back(back(os.path.abspath(__file__))))
if sources not in sys.path: sys.path.append(sources)

from common_lib.cache import Cache
from common_lib.read_config import enabled_modules


run_tagger_cmd = 'java -XX:ParallelGCThreads=2 -Xmx500m -jar ark-tweet-nlp-0.3.2.jar'
ark_sources = enabled_modules['ark_tweet']
if ark_sources:
    if ark_sources not in sys.path: sys.path.append(ark_sources)
    import CMUTweetTagger
    run_tagger_cmd = 'java -XX:ParallelGCThreads=2 -Xmx500m -jar {0}'.format(os.path.join(enabled_modules['ark_tweet'], 'ark-tweet-nlp-0.3.2.jar'))


class ArkTweetNLP:

    def __init__(self, data=[]):
        # Lookup cache (constantly rerunning tagger takes time)
        self.cache = Cache('ark_tweet')

        # Unescape data
        self.h = HTMLParser()

        # Resolve and cache all currently uncached tweets
        self.resolve(data)


    def normalizeKey(self, tweet):
        clean = lambda txt: self.h.unescape(txt).strip()
        try:
            tmp = tweet.decode('utf-8')
        except UnicodeEncodeError, e:
            # Didn't want to resort to this, but get each character one at a time
            ctmp = []
            for c in tweet:
                try:
                    c.decode('utf-8')
                    ctmp.append(c)
                except UnicodeEncodeError, e:
                    continue
            tmp = ''.join(ctmp)
        return clean(clean(tmp))


    def resolve(self, original):

        #print 'resolve length: ', len(original)

        data = [self.normalizeKey(twt) for twt in set(original)]

        if enabled_modules['caches'] is not None:
            # Tag all uncached data
            uncached = [ twt for twt in data if not self.cache.has_key(twt) ]
        else:
            uncached = data

        #print uncached
        #print 'len     : ', len(uncached)
        #print 'uncached: '
        #for twt in uncached: print '\t', twt
        #print '\n\n\n'

        partial = []
        if uncached:
            print 'uncached: ', len(uncached)
            partial = CMUTweetTagger.runtagger_parse(uncached, run_tagger_cmd=run_tagger_cmd)
            print 'partial: ', len(partial)

            if enabled_modules['caches'] is not None:
                for twt, tag in zip(uncached, partial):
                    #print 'adding: ', twt
                    self.cache.add_map(twt, tag)


        # Lookup all tags
        if enabled_modules['caches'] is not None:
            tagged = [ self.cache.get_map(twt) for twt in data ]
        else:
            tagged = partial

        #print 'TAGGED DATA'
        #print tagged

        # Store the data in the object
        self._toks = {}
        self._pos  = {}
        for twt,tags in zip(data, tagged):

            # Last step of splitting compund words
            newToks,newTags = self.post_process_tokenize(tags)

            self._toks[twt] = newToks
            self._pos[twt]  = newTags
            #print 'tweet:    ', twt
            #print 'words:    ', self._toks[twt]
            #print 'POS:      ', self._pos[twt]
            #print

        #if self._toks: exit()


    def post_process_tokenize(self, tags):

        oldToks = [ t[0] for t in tags ]
        oldTags = [ t[1] for t in tags ]

        newToks = []
        newTags = []

        p = False
        for tok,tag in zip(oldToks,oldTags):

            # Case: abbreviations
            if tok == 'w/':
                newToks.append('with')
                newTags.append(tag   )

            # Case: Attached-with  ex. "w/Biden"
            elif tok[:2] == 'w/':
                newToks.append('with' )
                newTags.append(  'P'  )
                newToks.append(tok[2:])
                newTags.append(tag    )

            # Case: compouund word, separated with /
            elif ( ('/' in tok)               and
                   (not is_url(tok))          and
                   (len(tok.split('/')[0])>2) and
                   (len(tok.split('/')[1])>2)   ):
                subs = tok.split('/')
                newToks.append(subs[0])
                newTags.append(tag    )  # assume same POS
                for subTok in subs[1:]:
                    newToks.append('/')
                    newTags.append(',')  # don't forget the '/' separates them

                    newToks.append(subTok)
                    newTags.append(   tag)  # assume same POS
                #p = True
                #print tok
                #print newToks
                #print

            # Case: default
            else:
                newToks.append(tok)
                newTags.append(tag)
        if p:
            print oldToks
            print newToks
            print

        return newToks,newTags



    def update(self, data):

        """
        update()

        Purpose: Run the tagger on a batch of tweets (rather than individually)

        @param data. A list of strings (each string is the text of a tweet)
        """
        self.resolve(data)
        #exit()



    def tokens(self, txt):
        key = self.normalizeKey(txt)
        return self._toks[key]


    def posTags(self, txt):
        key = self.normalizeKey(txt)
        return self._pos[key]


    def features(self, twt):

        """
        features()

        Purpose: Get twitter_nlp features

        @param twt.  The string text of a tweet.
        @return      A feature dictionary.
        """

        # Feature dictionary
        feats = {}

        # Escape text if not already done
        twt = self.normalizeKey(twt)

        # Feature: POS counts
        pos_counts = defaultdict(lambda:0)
        for pos in self._pos[twt]:
            if pos not in string.punctuation:
                pos_counts[pos] += 1
        for pos,count in pos_counts.items():
            featname = 'pos_count-%s' % pos
            feats[featname] = count

        #print 'ARK: ', twt
        #print '\t', feats

        return feats




def is_url(word):

    """
    isUrl()

    Purpose: Determine if a word is a URL

    @param word.   Any word from a tweet
    @return        A boolean indicating True is 'word' is a URL, false otherwise
    """

    if word[:7]  == 'http://': return True
    if word[:4]  == 'www.'   : return True
    if '.com' in word: return True
    if '.net' in word: return True
    if '.org' in word: return True

    return False




def main():

    # Parse arguments
    parser = argparse.ArgumentParser(description='twitter_nlp tagging')

    parser.add_argument('-t',
                        dest = 'tweets',
                        default = None,
                        type=argparse.FileType('r')
                       )

    args = parser.parse_args()


    # Read data from file
    twts = [ line.split('\t')[3].strip('\n')  for  line  in  args.tweets.readlines() ]

    # Run twitter_nlp on data
    t_nlp = ArkTweetNLP(twts)

    # Display tokenized data
    toks = [ t_nlp.tokens(twt)  for  twt  in  twts ]




# Reminder for self: Pizza in Olsen 311 - don't forget
if __name__ == '__main__':
    main()
