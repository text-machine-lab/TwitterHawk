#-------------------------------------------------------------------------------
# Name:        features.py
#
# Purpose:     Extract features
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import os, sys
import re
from copy import copy

import note

#from nltk.corpus import wordnet as wn   
#import Queue


from taskb_lexicon_features import lexicon_features



# Add common-lib code to system path
sources = os.getenv('BISCUIT_DIR')
if sources not in sys.path: sys.path.append(sources)
from common_lib.read_config                  import enabled_modules
from common_lib.common_lexicons              import emoticons
from common_lib.common_features              import utilities
from common_lib.common_features              import hashtag
from common_lib.common_features              import url
from common_lib.common_features.ark_tweet    import ark_tweet
from common_lib.common_features.twitter_data import twitter_data
from common_lib.common_features.ukb          import ukb_wsd


class FeaturesWrapper:

    def __init__(self):

        # Tag/Chunk data with ark_tweet_nlp
        if enabled_modules['ark_tweet']:
            self.ark_tweet = ark_tweet.ArkTweetNLP()
        else:
            self.ark_tweet = None

        # Lookup tweet metadata
        if enabled_modules['twitter_data']:
            self.twitter_data = twitter_data.TwitterData()

        # Get HTML data from URLs in tweets
        if enabled_modules['url']:
            self.url = url.Url()

        self.ukb = ukb_wsd.ukbWSD()



    def extract_features(self, X):

        """
        Model::extract_features()

        Purpose: Generate features for the input data

        @param notes. A list of note objects that store the tweet data
        @return       A list of feature dictionaries
        """

        # data   - A list of strings
        sids = [ x[0] for x in X ]
        data = [ x[1] for x in X ]

        # Batch retrieval of twitter metadata
        if enabled_modules['twitter_data']:
            self.twitter_data.resolve(sids, data)

        # Remove weird characters
        data = [ unicode(d.decode('utf-8')) for d in data ]

        # Batch update of external modules
        if enabled_modules['ark_tweet'   ]:
            self.ark_tweet.resolve( data)

        # Get features for each tweet
        features_list= [ self.features_for_tweet(t,s) for t,s in zip(data,sids) ]

        return features_list



    def features_for_tweet(self, tweet, sid):

        """
        Model::features_for_tweet()

        Purpose: Generate features for a single tweet

        @param tweet. A string (the text of a tweet)
        @param sid.   An int   (the ID   of a tweet)
        @param tags.  A list of data (POS and chunk tags) from twitter_nlp
        @return       A hash table of features
        """

        # Feature dictionary
        features = {}


        # Tweet representation (list of tokens/strings)
        phrase = utilities.tokenize(tweet, self.ark_tweet)


        # Feature: Stemmed Tokens
        normalized_stems = utilities.normalize_phrase_TaskB(phrase, stem=True)
        for word in normalized_stems:
            features[('stemmed_unigram_tok', word)] = 1


        # Feature: twitter_data features
        if enabled_modules['twitter_data']:
            tdata_feats = self.twitter_data.features(sid)
            features.update(tdata_feats)


        


        # Feature: Lexicon Features
        if enabled_modules['lexicons']:
            feats = lexicon_features(phrase)
            features.update(feats)


        # Feature: ark_tweet features (cached based on unescaped text)
        if enabled_modules['ark_tweet']:
            ark_feats = self.ark_tweet.features(tweet)
            features.update(ark_feats)


        """
        #add wordnet features     
        wnQueue = Queue.Queue()
        for word in phrase:
            parentNumber = 0
            synsetList = wn.synsets(word)
            wnQueue.put(synsetList)
            while wnQueue.empty() == False:
                queueList = wnQueue.get()
                if parentNumber > 0:
                    parentList = []
                    for synset in queueList:
                        features[('term_wn_node',synset.name)] = 1
                        parentList += synset.hypernyms()
                    wnQueue.put(parentList)
                    parentNumber = parentNumber - 1
                else:
                    for synset in queueList:
                        features[('term_wn_node',synset.name)] = 1
        """

        # Feature: URL Features
        if enabled_modules['url']:
            urls = [  w  for  w  in  phrase  if  utilities.is_url(w)  ]
            for url in urls:
                feats = self.url.features(url)
                features.update(feats)



        # Feature: Split hashtag
        if enabled_modules['hashtag']:
            hashtags = [ w for w in normalized_stems if len(w) and (w[0]=='#') ]
            for ht in hashtags:
                toks = hashtag.split_hashtag(ht)
                for tok in toks:
                    features[('hashtag-tok',tok.lower())] = 1


        # Feature: Punctuation counts
        text = ' '.join(phrase)
        for c in '!?':
            features['%s-count'  %c] = len(text.split(c)) - 1
            #features['%s-streaks'%c] = len(re.findall('[^\\%s]\\%s'%(c,c),text))


        # Result: Slightly better
        features['phrase_length'] = len(phrase) / 4

        if enabled_modules['ark_tweet']:
            #add ukb wsd features
            if self.ukb.cache.has_key( tweet ):
                wordSenses = self.ukb.cache.get_map( tweet )
            else:
                #print tweet
                wordSenses = self.ukb.ukb_wsd( phrase , self.ark_tweet.posTags( tweet ) )
                self.ukb.cache.add_map( tweet , wordSenses )
                
            for ws in wordSenses:
                for s in ws:
                    if ('wsd',s[0]) in features.keys():
                        features[('wsd',s[0])] += s[1]
                    else:
                        features[('wsd',s[0])] = s[1]

            


        '''
        # Result: Good :)
        # Feature: Contains long word? (boolean)
        long_word_threshold = 8
        contains_long_word = False
        for word in phrase:
            if len(word) > long_word_threshold:
                contains_long_word = True
                break
        features[ ('contains_long_word',contains_long_word) ] = 1
        '''

        '''
        print '\n\n'
        print phrase

        # Result: Worse (except for 3-grams with .5 weight)
        # Features: N-grams
        vals = [2,3,4]
        #vals = [3]
        for n in vals:
            for i in range(len(phrase)-n+1):

                #print '\t', normalized[i:i+n]
                ngram = phrase
                ngram = [ w.replace("\\","\\\\") for w in ngram[i:i+n] ]
                ngram = [ w.replace("'","\\'")   for w in ngram        ]
                
                tup = eval( "('" + "', '".join(ngram) + "')" )
                featname = ( '%d-gram'%n, tup  )
                features[featname] = .5
                print
                print '\t', ngram

                for j in range(1,n-1):
                    words = copy(ngram)
                    words[j] = '*'
                    tup = eval( "('" + "', '".join(words) + "')" )
                    featname = ( 'noncontiguous-%d-gram'%n, tup  )
                    features[featname] = 1
                    print '\t\t', tup
        '''


        '''
        # Result: Worse
        # Feature: Prefixes and Suffixes
        n = [2,3]
        for i,word in enumerate(normalized):
            for j in n:
                if word[-4:] == '_neg': word = word[:-3]

                prefix = word[:j]
                suffix = word[-1-j+1:]

                features[ ('prefix',prefix) ] = 1
                features[ ('suffix',suffix) ] = 1
        '''


        '''
        # Rating: Not effective for this data, which has virtually no emoticons
        # Feature: Emoticon Counts
        elabels = { 'positive':0, 'negative':0, 'neutral':0 }
        for word in phrase:
            elabel = emoticons.emoticon_type(word)
            if elabel:
                elabels[elabel] += 1
        for k,v in elabels.items():
            featname = k + '-emoticon'
            features[featname] = v
            #print featname, ' - ', v
        #print ''
        '''


        '''
        # Not useful
        # Feature: All Capitalization? (boolean)
        is_all_capitalization = True
        for word in phrase:
            if not word: continue
            if word[0].islower():
                is_all_capitalization = False
                break
        features[ ('all_capitalization',is_all_capitalization) ] = 1
        '''


        '''
        # Result: Worse
        # Feature: Contains elongated long punctuation? (boolean)
        contains_elongated_punc = False
        for word in phrase:
            if utilities.isElongatedPunctuation(word):
                contains_elongated_punc = True
                break
        features[ ('contains_elongated_punc',contains_elongated_punc) ] = 1
        '''


        #print '\n\n\n'
        #print tweet
        #print
        #print features

        return features


