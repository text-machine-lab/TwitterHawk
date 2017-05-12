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
from collections import defaultdict

import note

from nltk.corpus import wordnet as wn
import nltk.stem
import Queue


from taskb_lexicon_features import lexicon_features
import tf_idf
import spell



# Add common-lib code to system path
back = os.path.dirname
sources = back(back(back(back(os.path.abspath(__file__)))))
if sources not in sys.path: sys.path.append(sources)
from common_lib.read_config                  import enabled_modules
from common_lib.common_lexicons              import emoticons
from common_lib.common_features              import utilities
from common_lib.common_features              import hashtag
from common_lib.common_features.ark_tweet    import ark_tweet


st = nltk.stem.PorterStemmer()


MIN_COUNT = 2
MAX_COUNT = 600


# debug info
seen = set()


class FeaturesWrapper:

    def __init__(self):

        # Tag/Chunk data with ark_tweet_nlp
        if enabled_modules['ark_tweet']:
            self.ark_tweet = ark_tweet.ArkTweetNLP()
        else:
            self.ark_tweet = None

        # Count all token frequencies
        tf_idf._build_dictionary(self.ark_tweet, enabled_modules['twitter_data'])

        # Spelling correction
        self.speller = spell.SpellChecker()




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

        # Remove weird characters
        #data = [ unicode(d.decode('utf-8')) for d in data ]

        # Batch update of external modules
        if enabled_modules['ark_tweet'   ]:
            self.ark_tweet.resolve(data)

        # Get features for each tweet
        features_list= [ self.features_for_tweet(t,s) for t,s in zip(data,sids) ]

        return features_list



    def features_for_tweet(self, tweet, sid):

        """
        Model::features_for_tweet()

        Purpose: Generate features for a single tweet

        @param tweet. A string (the text of a tweet)
        @param sid.   An int   (the ID   of a tweet)
        @return       A hash table of features
        """

        # Feature dictionary
        features = {}

        # POS list
        if enabled_modules['ark_tweet']:
            pos = self.ark_tweet.posTags(tweet)
        else:
            pos = None

        # Tweet representation (list of tokens/strings)
        phrase = utilities.tokenize(tweet, self.ark_tweet)


        #'''
        # Feature: Unedited Unigram Tokens
        for tok in phrase:
            if tok == '': continue
            if tf_idf.doc_freq(tok) < MIN_COUNT: continue
            if tok in tf_idf.stop_words:         continue
            features[('unedited-uni-tok',tok)] = 1
        #'''

        # Edit misspellings
        unis = self.speller.correct_spelling(phrase, pos)

        # Flatten from multi-word tokens
        if pos:
            flattened = []
            flat_pos = []
            for tok,tag in zip(unis,pos):
                for w in tok.split():
                    flattened.append(w)
                    flat_pos.append(tag)
        else:
            flattened = unis
            flat_pos  = None


        # Normalize sentence
        normalized = utilities.normalize_phrase_TaskB(flattened)


        # Feature: Processed Unigram Tokens
        uni_freqs = defaultdict(lambda:0)
        for i,word in enumerate(normalized):

            if word == '': continue
            w = word if (word[-4:]!='_neg') else word[:-4]
            if tf_idf.doc_freq(w) < MIN_COUNT: continue
            if w in tf_idf.stop_words:         continue

            # Exclude proper nouns and prepositions
            if flat_pos:
                if flat_pos[i] == '^': continue
                if flat_pos[i] == 'Z': continue
                if flat_pos[i] == 'P': continue
                if flat_pos[i] == 'O': continue
                uni_freqs[word] += 1
            else:
                uni_freqs[word] += 1

        feats = defaultdict(lambda:0)
        for key,tf in uni_freqs.items():
            word = key
            if word[-4:] == '_neg':
                word = word[:-4]
                score = -1
            else:
                score = 1
            feats[('uni_tok'     ,        word) ] += score
            feats[('uni_stem_tok',st.stem(word))] += score
        features.update(feats)

        #return features

        #'''
        # Feature: Split hashtag
        if enabled_modules['hashtag']:
            hashtags = [ w for w in normalized if len(w) and (w[0]=='#') ]
            for ht in hashtags:
                toks = hashtag.split_hashtag(ht)
                if (ht not in seen) and (ht not in hashtag.annotations):
                    seen.add(ht)
                    #print ht, '\t', toks
                for tok in utilities.normalize_phrase_TaskB(toks):
                    if tok[-4:] == '_neg':
                        tok = tok[:-4]
                        score = -1
                    else:
                        score = 1
                    if len(tok) > 2:
                        if tf_idf.doc_freq(tok) < MIN_COUNT: continue
                        if tok in tf_idf.stop_words:         continue
                        features[('uni_tok'     ,        tok) ] = score
                        features[('uni_stem_tok',st.stem(tok))] = score
        #'''

        #return features

        # Feature: Lexicon Features
        if enabled_modules['lexicons']:
            feats = lexicon_features(normalized)
            features.update(feats)

        #return features

        # Feature: Punctuation counts
        for c in '!?':
            val = tweet.count(c)
            if val > 0:
                features['%s-count' % c] = val


        # Features: Text lengths
        #features['phrase_length']   = len(tweet) / 140.0


        # Feature: Contains long word? (boolean)
        long_word_threshold = 8
        contains_long_word = False
        for word in phrase:
            if len(word) == 0: continue
            if word[0] == '@': continue
            if len(word) > long_word_threshold:
                contains_long_word = True
                break
        if contains_long_word:
            features['contains_long_word'] = 1


        # Feature: Emoticon Counts
        elabels = { 'positive':0, 'negative':0, 'neutral':0 }
        for word in phrase:
            elabel = emoticons.emoticon_type(word)
            if elabel:
                elabels[elabel] += 1
        for k,v in elabels.items():
            if v > 0:
                featname = k + '-emoticon'
                features[featname] = v


        # Features: contains twitter-specific features (hashtags & mentions)
        contains_hashtag = False
        contains_mention = False
        for tok in phrase:
            if tok == '': continue
            if tok[0] == '@': contains_mention = True
            if tok[0] == '#': contains_hashtag = True
        if contains_hashtag: features['contains_hashtag'] = 1
        if contains_mention: features['contains_mention'] = 1


        #return features


        # Feature: Bigram Tokens
        flattened = []
        for tok in normalized:
            flattened += tok.split()
        for i in range(len(flattened)-1):
            bigram  = tuple(flattened[i:i+2])

            # short circuits
            if any(w == ''                        for w in bigram): continue
            if any(tf_idf.doc_freq(w) < MIN_COUNT for w in bigram): continue
            if any(w in tf_idf.stop_words         for w in bigram): continue

            # context
            t1,t2 = bigram
            if t1[-4:] == '_neg':
                t1 = t1[:-4]
                score = -1
            else:
                score = 1
            if t2[-4:] == '_neg':
                t2 = t2[:-4]

            sbigram = (st.stem(t1),st.stem(t2))
            features[( 'bigram_tok',(t1,t2))] = score
            features[('sbigram_tok',sbigram)] = score

        return features


        # Feature: Trigram Tokens
        for i in range(len(flattened)-2):
            trigram  = tuple(flattened[i:i+3])
            if any(w == '' for w in trigram): continue
            if any(tf_idf.doc_freq(phrase[i]) < MIN_COUNT for w in range(3)): continue
            if phrase[i] in tf_idf.stop_words:      continue
            t1,t2,t3 = trigram
            if t1[-4:] == '_neg':
                t1 = t1[:-4]
                score = -1
            else:
                score = 1
            if t2[-4:] == '_neg':
                t2 = t2[:-4]
            if t3[-4:] == '_neg':
                t3 = t3[:-4]

            features[('trigram_tok',trigram)] = 1
            #features[('strigram_tok',strigram)] = 1

        return features

        # Feature: ark_tweet features (cached based on unescaped text)
        if enabled_modules['ark_tweet']:
            ark_feats = self.ark_tweet.features(tweet)
            features.update(ark_feats)


        return features

