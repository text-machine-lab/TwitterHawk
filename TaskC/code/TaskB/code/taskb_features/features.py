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

from nltk.corpus import wordnet as wn   
import Queue


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
from common_lib.common_features.ukb          import ukb_wsd


class FeaturesWrapper:

    def __init__(self):

        # Tag/Chunk data with ark_tweet_nlp
        if enabled_modules['ark_tweet']:
            self.ark_tweet = ark_tweet.ArkTweetNLP()
        else:
            self.ark_tweet = None

        # Get HTML data from URLs in tweets
        if enabled_modules['url']:
            self.url = url.Url()

        if enabled_modules['ukb_wsd']:
            self.ukb = ukb_wsd.ukbWSD()



    def extract_features(self, X):

        """
        Model::extract_features()

        Purpose: Generate features for the input data

        @param notes. A list of note objects that store the tweet data
        @return       A list of feature dictionaries
        """

        # data   - A list of strings
        data = X

        # Remove weird characters
        data = [ unicode(d.decode('utf-8')) for d in data ]

        # Batch update of external modules
        if enabled_modules['ark_tweet']:
            self.ark_tweet.resolve( data)

        # Get features for each tweet
        features_list= [ self.features_for_tweet(t) for t in data ]

        return features_list



    def features_for_tweet(self, tweet):

        """
        Model::features_for_tweet()

        Purpose: Generate features for a single tweet

        @param tweet. A string (the text of a tweet)
        @return       A hash table of features
        """

        # Feature dictionary
        features = {}


        # Tweet representation (list of tokens/strings)
        phrase = utilities.tokenize(tweet, self.ark_tweet)


        # Feature: Unigram Tokens
        normalized = utilities.normalize_phrase_TaskB(phrase)
        for word in normalized:
            features[('unigram_tok', word)] = 1


        # Feature: Lexicon Features
        if enabled_modules['lexicons']:
            feats = lexicon_features(phrase)
            features.update(feats)


        # Feature: ark_tweet features (cached based on unescaped text)
        if enabled_modules['ark_tweet']:
            ark_feats = self.ark_tweet.features(tweet)
            features.update(ark_feats)


        # Feature: Punctuation counts
        text = ' '.join(phrase)
        for c in '!?':
            features['%s-count'  %c] = len(text.split(c)) - 1
            #features['%s-streaks'%c] = len(re.findall('[^\\%s]\\%s'%(c,c),text))


        # Result: Slightly better
        features['phrase_length'] = len(phrase) / 4


        # Feature: Contains long word? (boolean)
        long_word_threshold = 8
        contains_long_word = False
        for word in phrase:
            if len(word) > long_word_threshold:
                contains_long_word = True
                break
        features[ ('contains_long_word',contains_long_word) ] = 1


        # Feature: Prefixes and Suffixes
        n = [2,3]
        for i,word in enumerate(normalized):
            for j in n:
                if word[-4:] == '_neg': word = word[:-3]

                prefix = word[:j]
                suffix = word[-1-j+1:]

                features[ ('prefix',prefix) ] = 1
                features[ ('suffix',suffix) ] = 1


        # Feature: Emoticon Counts
        elabels = { 'positive':0, 'negative':0, 'neutral':0 }
        for word in phrase:
            elabel = emoticons.emoticon_type(word)
            if elabel:
                elabels[elabel] += 1
        for k,v in elabels.items():
            featname = k + '-emoticon'
            features[featname] = v


        #print '\n\n\n'
        #print tweet
        #print
        #print features

        return features


