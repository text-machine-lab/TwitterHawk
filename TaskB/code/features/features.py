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
from HTMLParser import HTMLParser

import utilities
from nlp          import nlp
from twitter_data import twitter_data

import note
from read_config import enabled_modules


# Add lexicon code to path
if enabled_modules['lexicons']:
    from lexicon import lexicon_features
    sys.path.append( os.path.join(enabled_modules['lexicons'] ,'code') )
else:
    sys.path.append( os.path.join(os.getenv('BISCUIT_DIR') ,'lexicons/code') )
import emoticons


if enabled_modules['hashtag']:
    sys.path.append(enabled_modules['hashtag'])
    import hashtag


class FeaturesWrapper:

    def __init__(self):
        pass



    def extract_features(self, notes):

        """
        Model::extract_features()

        Purpose: Generate features for the input data

        @param notes. A list of note objects that store the tweet data
        @return       A list of feature dictionaries
        """

        # data   - A list of list of the medical text's words
        data = [ twt for note in notes for twt in note.text_list() ]
        sids = [ sid for note in notes for sid in note.sid_list()  ]

        # Process data with twitter_nlp
        tagger = enabled_modules['twitter_nlp']
        if tagger:
            self.twitter_nlp = nlp.TwitterNLP(tagger, data)

        # Lookup tweet metadata
        if enabled_modules['twitter_data']:
            self.twitter_data = twitter_data.TwitterData(sids)

        # Get features for each tweet
        features_list= [ self.features_for_tweet(s,t) for s,t in zip(sids,data) ]

        return features_list



    def features_for_tweet(self, sid, tweet):

        """
        Model::features_for_tweet()

        Purpose: Generate features for a single tweet

        @param sid.   An int   (the ID   of a tweet)
        @param tweet. A string (the text of a tweet)
        @param tags.  A list of data (POS and chunk tags) from twitter_nlp
        @return       A hash table of features
        """

        # Feature dictionary
        features = {}


        # Feature: twitter_nlp features
        if enabled_modules['twitter_nlp']:
            nlp_feats = self.twitter_nlp.features(tweet)
            features.update(nlp_feats)


        # Feature: twitter_nlp features
        if enabled_modules['twitter_data']:
            tdata_feats = self.twitter_data.features(sid)
            features.update(tdata_feats)


        # Tweet representation
        h = HTMLParser()
        tweet = h.unescape(tweet)
        phrase = tweet.split(' ')


        # Feature: Lexicon Features
        if enabled_modules['lexicons']:
            feats = lexicon_features(phrase)
            features.update(feats)


        # Feature: Normalized unigrams
        normalized_stems = utilities.normalize_phrase(phrase, stem=True)
        for word in normalized_stems:
            features[('term_unigram', word)] = 1.5


        '''
        print phrase
        print
        print normalized
        '''


        # Feature: Split hashtag
        if enabled_modules['hashtag']:
            hashtags = [  w  for  w  in  phrase  if  len(w) and (w[0] == '#')  ]
            for ht in hashtags:
                toks = hashtag.split_hashtag(ht)
                #print ht
                #print '\t', toks
                #print
                for tok in toks:
                    features[('hashtag-tok',tok.lower())] = 1

            #if hashtags: print


        # Feature: Punctuation counts
        text = ' '.join(phrase)
        for c in '!?':
            features['%s-count'  %c] = len(text.split(c)) - 1
            #features['%s-streaks'%c] = len(re.findall('[^\\%s]\\%s'%(c,c),text))


        # Result: Slightly better
        features['tweet_length'] = len(' '.join(phrase))
        features['phrase_length'] = len(phrase) / 15


        #print features


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
        # Result: Worse
        # Features: N-grams
        vals = [2,3,4]
        for n in vals:
            for i in range(len(phrase)-n+1):

                #print '\t', normalized[i:i+n]
                ngram = phrase
                ngram = [ w.replace("\\","\\\\") for w in ngram[i:i+n] ]
                ngram = [ w.replace("'","\\'")   for w in ngram        ]
                
                tup = eval( "('" + "', '".join(ngram) + "')" )
                featname = ( '%d-gram'%n, tup  )
                features[featname] = 1
                #print '\t', ngram

                for j in range(n):
                    words = copy(ngram)
                    words[j] = '*'
                    tup = eval( "('" + "', '".join(words) + "')" )
                    featname = ( 'noncontiguous-%d-gram'%n, tup  )
                    features[featname] = 1
                    #print tup
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

        return features


