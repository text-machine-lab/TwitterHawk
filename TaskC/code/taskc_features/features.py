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


from taskc_lexicon_features import lexicon_features
from ark_tweet import ark_tweet
import utilities


# Add common-lib code to system path
sources = os.getenv('BISCUIT_DIR')
if sources not in sys.path: sys.path.append(sources)
from common_lib.read_config                  import enabled_modules
from common_lib.common_lexicons              import emoticons

from TaskC.code.TaskB.code.predict import predict_full_tweet_sentiment




st = nltk.stem.SnowballStemmer('english')



class FeaturesWrapper:

    def __init__(self):

        self.ark_tweet = ark_tweet.ArkTweetNLP()



    def extract_features(self, X):

        """
        Model::extract_features()

        Purpose: Generate features for the input data

        @param notes. A list of note objects that store the tweet data
        @return       A list of feature dictionaries
        """

        # data   - list of (begin, end, split_sentence) tuples
        data = X

        # Remove weird characters
        text = [ ' '.join(t[2]) for t in data ]
        text = [ unicode(t.decode('utf-8')) for t in text ]

        # Batch update of external modules
        self.ark_tweet.resolve(text)

        # Batch tweet-level sentiment classification
        print '<TaskB>'
        tweet_labels = predict_full_tweet_sentiment(text)
        print '</TaskB>'
        self.tweet_labels = {}
        for txt,label in zip(text,tweet_labels):
            self.tweet_labels[txt] = label

        # Get features for each tweet
        features_list= [ self.features_for_tweet(t) for t in data ]

        return features_list



    def features_for_tweet(self, tweet_repr):

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


        # Feature Dictionary
        features = {}


        # Normalize all text (tokenizer, stem, etc)
        normalized =utilities.normalize_phrase(sentence,ark_tweet=self.ark_tweet)
        norm_sentence = [ w for words in normalized for w in words ]


        # Unigram context window
        window = 3
        prefix_start = max(begin-window, 0)
        context = sentence[prefix_start:end+1+window]


        # Useful for local and global features
        texts   = [sentence  , context  ]
        labels  = ['sentence', 'context']
        weights = [ 0.5      , 1.0      ]   


        # Tweet-level label from Task B classifier
        text = ' '.join(sentence)
        text = unicode(text.decode('utf-8'))
        tweet_label = self.tweet_labels[text]
        features[('tweet-level',tweet_label)] = 1

        # Sentence unigrams
        for toks in normalized:
            for word in toks:
                if word[-4:] == '_neg':
                    stemmed = st.stem(word[:-4]) + '_neg'
                else:
                    stemmed = st.stem(word)
                features[('sentence_unigram', word )] = weights[0]
                features[('stemmed_sentence_unigram', stemmed)] = weights[0]
            

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
            # Leading context
            #prev_lex_feats = lexicon_features(sentence,prefix_start,end+1+window, ark_tweet=self.ark_tweet)
            #prev_lex_feats = {('prev-'+k[0],k[1]):v for k,v in prev_lex_feats.items()}
            #features.update(prev_lex_feats)

            # Trailing context
            #next_lex_feats = lexicon_features(sentence,end+1,end+1+window, ark_tweet=self.ark_tweet)
            #next_lex_feats = {('next-'+k[0],k[1]):v for k,v in next_lex_feats.items()}
            #features.update(next_lex_feats)

            # Full tweet
            full_lex_feats = lexicon_features(sentence,0,len(sentence), ark_tweet=self.ark_tweet)
            next_lex_feats = {('full-'+k[0],k[1]):0.5*v for k,v in full_lex_feats.items()}
            features.update(full_lex_feats)

            #print lex_feats
            #print prev_lex_feats
            #print next_lex_feats


        # Feature: Emoticon Counts
        for text,label,weight in zip(texts,labels,weights):
            elabels = defaultdict(lambda:0)
            for word in text:
                elabel = emoticons.emoticon_type(word)
                if elabel:
                    elabels[elabel] += 1
            for k,v in elabels.items():
                featname = label + '-' + k + '-emoticon'
                features[featname] = weight * v


        # Feature: Punctuation counts
        for text,label,weight in zip(texts,labels,weights):
            punct = {'!':0, '?':0}
            for c in ''.join(text):
                if c in punct: punct[c] += 1
            for k,v in punct.items():
                featname = label + '-' + k + '-count'
                features[featname] = weight * v


        #print sentence
        #print sentence[begin:end+1]
        #print features
        #print '\n\n'


        return features

