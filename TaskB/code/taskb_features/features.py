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

from taskb_lexicon_features import lexicon_features


# Add common-lib code to system path
sources = os.getenv('BISCUIT_DIR')
if sources not in sys.path: sys.path.append(sources)

from common_lib.read_config                  import enabled_modules

from common_lib.common_lexicons              import emoticons

from common_lib.common_features              import utilities
from common_lib.common_features              import hashtag
from common_lib.common_features              import url
from common_lib.common_features.nlp          import nlp
from common_lib.common_features.twitter_data import twitter_data



class FeaturesWrapper:

    def __init__(self):

        # Tag/Chunk data with twitter_nlp
        tagger = enabled_modules['twitter_nlp']
        if tagger:
            self.twitter_nlp = nlp.TwitterNLP(tagger)
        else:
            self.twitter_nlp = None

        # Lookup tweet metadata
        if enabled_modules['twitter_data']:
            self.twitter_data = twitter_data.TwitterData()

        # Get HTML data from URLs in tweets
        if enabled_modules['url']:
            self.url = url.Url()



    def extract_features(self, X):

        """
        Model::extract_features()

        Purpose: Generate features for the input data

        @param notes. A list of note objects that store the tweet data
        @return       A list of feature dictionaries
        """

        # data   - A list of list of the medical text's words
        sids = [ x[0] for x in X ]
        data = [ x[1] for x in X ]

        # Batch update of external modules
        if enabled_modules['twitter_nlp' ]:
            self.twitter_nlp.resolve( data)
        if enabled_modules['twitter_data']:
            self.twitter_data.resolve(sids)

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


        # Feature: twitter_nlp features (cached based on unescaped text)
        if enabled_modules['twitter_nlp']:
            nlp_feats = self.twitter_nlp.features(tweet)
            features.update(nlp_feats)


        # Tweet representation (list of tokens/strings)
        phrase = utilities.tokenize(tweet, self.twitter_nlp)


        # TODO - Work on normalization of tweet unigrams
        # Feature: Normalized unigrams
        normalized_stems = utilities.normalize_phrase_TaskB(phrase, stem=True)
        #print tweet
        for word in normalized_stems:
            #print '\t', word
            features[('term_unigram', word)] = 1
        #print


        # Feature: twitter_nlp features
        if enabled_modules['twitter_data']:
            tdata_feats = self.twitter_data.features(sid)
            features.update(tdata_feats)


        # Feature: URL Features
        if enabled_modules['url']:
            urls = [  w  for  w  in  phrase  if  utilities.is_url(w)  ]
            for url in urls:
                feats = self.url.features(url)
                features.update(feats)


        # Feature: Lexicon Features
        if enabled_modules['lexicons']:
            feats = lexicon_features(phrase)
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
        # Result: Worse (except for 3-grams with .5 weight)
        # Features: N-grams
        #vals = [2,3,4]
        vals = [3]
        for n in vals:
            for i in range(len(phrase)-n+1):

                #print '\t', normalized[i:i+n]
                ngram = phrase
                ngram = [ w.replace("\\","\\\\") for w in ngram[i:i+n] ]
                ngram = [ w.replace("'","\\'")   for w in ngram        ]
                
                tup = eval( "('" + "', '".join(ngram) + "')" )
                featname = ( '%d-gram'%n, tup  )
                features[featname] = .5
                #print '\t', ngram

                #for j in range(n):
                #    words = copy(ngram)
                #    words[j] = '*'
                #    tup = eval( "('" + "', '".join(words) + "')" )
                #    featname = ( 'noncontiguous-%d-gram'%n, tup  )
                #    features[featname] = 1
                #    #print tup
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


