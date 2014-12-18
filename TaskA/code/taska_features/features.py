#-------------------------------------------------------------------------------
# Name:        features.py
#
# Purpose:     Extract features from tweets
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------



import sys
import os
from collections import defaultdict
import string
import re
import nltk.stem


from taska_lexicon_features import lexicon_features
#import spell


# Add common-lib code to system path
sources = os.getenv('BISCUIT_DIR')
if sources not in sys.path: sys.path.append(sources)
from common_lib.read_config                  import enabled_modules
from common_lib.common_lexicons              import emoticons
from common_lib.common_features              import utilities
from common_lib.common_features.ark_tweet    import ark_tweet
from common_lib.common_features.twitter_data import twitter_data
from common_lib.common_features              import hashtag




st = nltk.stem.SnowballStemmer('english')



class FeaturesWrapper:

    def __init__(self):

        # Tag/Chunk data with ark_tweet_nlp
        if enabled_modules['ark_tweet']:
            self.ark_tweet = ark_tweet.ArkTweetNLP()
        else:
            self.ark_tweet = None

        # Spelling correction
        #self.speller = spell.SpellChecker()

        # Lookup tweet metadata
        if enabled_modules['twitter_data']:
            self.twitter_data = twitter_data.TwitterData()



    def extract_features(self, X):

        """
        Model::extract_features()

        Purpose: Generate features for the input data

        @param notes. A list of note objects that store the tweet data
        @return       A list of feature dictionaries
        """

        # data   - list of (text, begin, end) tuples
        sids = [ x[0] for x in X ]
        data = [ x[1] for x in X ]

        # Batch retrieval of twitter metadata
        if enabled_modules['twitter_data']:
            self.twitter_data.resolve(sids, data)

        # Remove weird characters
        text = [ ' '.join(t[2]) for t in data ]
        text = [ unicode(t.decode('utf-8')) for t in text ]

        # Batch update of external modules
        if enabled_modules['ark_tweet'   ]:
            self.ark_tweet.resolve(text)

        # Get features for each tweet
        features_list= [ self.features_for_tweet(t,s) for t,s in zip(data,sids) ]

        return features_list



    def features_for_tweet(self, tweet_repr, sid):

        """
        Model::features_for_tweet()

        Purpose: Generate features for a single tweet

        @param tweet. A 3-tuple representing a tweet
        @return       A hash table of features
        """

        # data
        begin    = tweet_repr[0]
        end      = tweet_repr[1]
        sentence = tweet_repr[2]
        phrase   = sentence[begin:end+1]


        #print phrase
        #return {}

        # Feature Dictionary
        features = {}


        # Normalize all text (tokenizer, stem, etc)
        normalized = utilities.normalize_phrase_TaskA(sentence,ark_tweet=self.ark_tweet)
        flat_normed = [ w for words in normalized for w in words ]


        # Unigram context window
        window = 3
        prefix_start = max(begin-window, 0)
        context = sentence[prefix_start:end+1+window]

        # Feature: unedited term unigrams
        for tok in phrase:
            if tok == '': continue
            if tok in utilities.stop_words:         continue
            features[('unedited-uni-tok',tok)] = 1


        # Term unigrams
        for tok in normalized[begin:end+1]:
            for word in tok:
                if word[-4:] == '_neg':
                    stemmed = st.stem(word[:-4]) + '_neg'
                else:
                    stemmed = st.stem(word)
                features[('term_unigram', word )] = 1
                features[('stemmed_term_unigram', stemmed)] = 1


        # Feature: Unigram context
        # Leading
        for tok in normalized[prefix_start:begin]:
            for word in tok:
                features[('leading_unigram', word)] = 1
        # Trailing
        for tok in normalized[end+1:end+1+window]:
            for word in tok:
                features[('trailing_unigram', word)] = 1


        # Feature: Lexicon Features
        if enabled_modules['lexicons']:
            #print '\n\n\n'
            #print 'LEX FEATS: ', sentence
            #print begin, end
            # Phrase in question
            lex_feats = lexicon_features(sentence,begin,end+1,ark_tweet=self.ark_tweet)
            features.update(lex_feats)

            # Leading context
            prev_lex_feats = lexicon_features(sentence,prefix_start,end+1+window, ark_tweet=self.ark_tweet)
            prev_lex_feats = {('prev-'+k[0],k[1]):v for k,v in prev_lex_feats.items()}
            features.update(prev_lex_feats)

            # Trailing context
            next_lex_feats = lexicon_features(sentence,end+1,end+1+window, ark_tweet=self.ark_tweet)
            next_lex_feats = {('next-'+k[0],k[1]):v for k,v in next_lex_feats.items()}
            features.update(next_lex_feats)

            #print lex_feats
            #print prev_lex_feats
            #print next_lex_feats


        # Feature: twitter_data features
        if enabled_modules['twitter_data']:
            tdata_feats = self.twitter_data.features(sid)
            features.update(tdata_feats)


        '''
        # Feature: Split hashtag
        if enabled_modules['hashtag']:
            hashtags = [ w for w in flat_normed if len(w) and (w[0]=='#') ]
            for ht in hashtags:
                toks = hashtag.split_hashtag(ht)
                #print ht, '\t', toks
                for tok in toks:
                    features[('hashtag-tok',tok.lower())] = 1

        '''

        # Feature: Split hashtag
        if enabled_modules['hashtag']:
            hashtags = [ w for w in flat_normed if len(w) and (w[0]=='#') ]
            for ht in hashtags:
                toks = hashtag.split_hashtag(ht)
                for tok in utilities.normalize_phrase_TaskB(toks):
                    if tok[-4:] == '_neg':
                        tok = tok[:-4]
                        score = -1
                    else:
                        score = 1
                    if len(tok) > 2:
                        if tok in utilities.stop_words: continue
                        features[('trailing_unigram'    ,        tok) ] = score
                        features[('stemmed_term_unigram',st.stem(tok))] = score

        #'''

        #print
        #print sentence
        #print begin
        #print end
        #print phrase

        # Features: Misc position data
        features['phrase'] = ' '.join(phrase)
        features['first_unigram'] = sentence[begin]
        features[ 'last_unigram'] = sentence[  end]
        features['phrase_length'] = len(' '.join(sentence)) / 140.0
        features['is_first'] = (begin == 0)
        features['is_last'] = (end == len(sentence)-1)


        # Feature: Whether every word is a stop word
        if all([ (len(tok) == 0) for tok in normalized[begin:end+1]]):
            features['all_stopwords'] = 1


        # Feature: All Caps? (boolean)
        if re.search('^[A-Z\\?!]*[A-Z][A-Z\\?!]*$',''.join(phrase)):
            features[ ('all_caps',None) ] = 1


        # Feature: Emoticon Counts
        elabels = defaultdict(lambda:0)
        for word in phrase:
            elabel = emoticons.emoticon_type(word)
            if elabel:
                elabels[elabel] += 1
        for k,v in elabels.items():
            featname = k + '-emoticon'
            features[featname] = v


        # Feature: Punctuation counts
        punct = {'!':0, '?':0}
        for c in ''.join(phrase):
            if c in punct: punct[c] += 1
        for k,v in punct.items():
            featname = k + '-count'
            features[featname] = v


        # Feature: Contains elongated long word? (boolean)
        contains_elongated_word = False
        for words in normalized:
            for word in words:
                if utilities.is_elongated_word(word):
                    contains_elongated_word = True
        features[ ('contains_elongated_word',contains_elongated_word) ] = 1


        # Feature: Contains long word? (boolean)
        long_word_threshold = 8
        contains_long_word = False
        for words in normalized:
            for word in words:
                if len(word) > long_word_threshold:
                    contains_long_word = True
        features[ ('contains_long_word',contains_long_word) ] = 1


        # Feature: Contains elongated long punctuation? (boolean)
        contains_elongated_punc = False
        for words in normalized:
            for word in words:
                if utilities.is_elongated_punctuation(word):
                    contains_elongated_punc = True
        features[ ('contains_elongated_punc',contains_elongated_punc) ] = 1


        # Officially removed: 
        #  1. character prefixes and suffixes
        #  2. whether every word begins with a captial letter
        #  3. bigrams and trigrams (from normalized phrase)


        return features

