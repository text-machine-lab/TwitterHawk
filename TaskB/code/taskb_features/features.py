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


st = nltk.stem.PorterStemmer()



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

        # Count all token frequencies
        tf_idf._build_dictionary(self.ark_tweet, os.path.join(os.getenv('BISCUIT_DIR'),'TaskB/etc/data'))

        # Spellinf correction
        self.speller = spell.SpellChecker()

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
        sids = [ x[0] for x in X ]
        data = [ x[1] for x in X ]

        # Batch retrieval of twitter metadata
        if enabled_modules['twitter_data']:
            self.twitter_data.resolve(sids, data)

        # Remove weird characters
        data = [ unicode(d.decode('utf-8')) for d in data ]

        # Batch update of external modules
        if enabled_modules['ark_tweet'   ]:
            self.ark_tweet.resolve(data)

        '''
        # Re-tokenize the newly spell corrected stuff
        if enabled_modules['ark_tweet'   ]:
            tweets = []
            for text in data:
                phrase = utilities.tokenize(text, self.ark_tweet)
                pos = self.ark_tweet.posTags(text)
                unis = self.speller.correct_spelling(phrase, pos)
                newSent = ' '.join(unis)
                tweets.append(newSent)
            self.ark_tweet.resolve(tweets)
        '''
        

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

        # POS list
        if enabled_modules['ark_tweet']:
            pos = self.ark_tweet.posTags(tweet)
        else:
            pos = None

        # Tweet representation (list of tokens/strings)
        phrase = utilities.tokenize(tweet, self.ark_tweet)
        unis = self.speller.correct_spelling(phrase, pos)
        #unis = phrase

        # Re-tokenize the newly spell corrected stuff
        #newSent = ' '.join(unis)
        #newToks = utilities.tokenize(tweet, self.ark_tweet)

        # Normalize sentence
        normalized = utilities.normalize_phrase_TaskB(unis)

        stemmed = []
        for word in normalized:
            if word[-4:] == '_neg': word = word[:-4]
            stemmed.append(st.stem(word))


        '''
        for w,u,n,s in zip(phrase,unis,normalized,stemmed):
            print w, '\t', u
            print '\t', n
            print '\t', s
            print
        print '\n'
        '''


        # Feature: Unigram Tokens
        uni_freqs = defaultdict(lambda:0)
        for i,word in enumerate(normalized):
            if word == '': continue
            if tf_idf.doc_freq(phrase[i]) <   3: continue
            if tf_idf.doc_freq(phrase[i]) > 900: continue
            if pos:
                # Exclude proper nouns
                if pos[i] != '^':
                    uni_freqs[(phrase[i],word)] += 1
            else:
                uni_freqs[(phrase[i],word)] += 1

        for key,tf in uni_freqs.items():
            orig,word = key
            if word[-4:] == '_neg':
                word = word[:-4]
                score = -1
            else:
                score = 1
            # upweight for caps
            #if orig.isupper():
            #    score *= 2
            features[('uni_tok'     ,        word) ] = score
            features[('uni_stem_tok',st.stem(word))] = score

        #for orig,corrected in zip(normalized,unis):
        #    print orig, '\t\t\t', corrected
        #print '-' * 20, '\n'


        #exit()

        # Feature: Bigram Tokens
        for i in range(len(normalized)-1):
            bigram  = tuple(normalized[i:i+2])
            sbigram = tuple(   stemmed[i:i+2])

            # short circuits
            if any(w == '' for w in bigram): continue
            if any(tf_idf.doc_freq(phrase[i]) <   3 for w in range(2)): continue
            if any(tf_idf.doc_freq(phrase[i]) > 900 for w in range(2)): continue

            # context 
            t1,t2 = bigram
            if t1[-4:] == '_neg': 
                t1 = t1[:-4]
                score = -1
            else:
                score = 1
            if t2[-4:] == '_neg': 
                t2 = t2[:-4]

            features[( 'bigram_tok',(t1,t2))] = score
            features[('sbigram_tok',sbigram)] = score


        # Feature: Trigram Tokens
        for i in range(len(unis)-2):
            trigram  = tuple(   unis[i:i+3])
            strigram = tuple(stemmed[i:i+3])
            if any(w == '' for w in trigram): continue
            if any(tf_idf.doc_freq(phrase[i]) <   3 for w in range(3)): continue
            if any(tf_idf.doc_freq(phrase[i]) > 900 for w in range(3)): continue

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
            features[('strigram_tok',strigram)] = 1



        # Feature: Lexicon Features
        if enabled_modules['lexicons']:
            feats = lexicon_features(phrase)
            features.update(feats)


        # Feature: ark_tweet features (cached based on unescaped text)
        if enabled_modules['ark_tweet']:
            ark_feats = self.ark_tweet.features(tweet)
            features.update(ark_feats)


        '''
        # Feature: twitter_data features
        if enabled_modules['twitter_data']:
            tdata_feats = self.twitter_data.features(sid)
            features.update(tdata_feats)


        # Feature: URL Features
        if enabled_modules['url']:
            urls = [  w  for  w  in  phrase  if  utilities.is_url(w)  ]
            for url in urls:
                feats = self.url.features(url)
                features.update(feats)


        # Feature: Split hashtag
        if enabled_modules['hashtag']:
            hashtags = [ w for w in normalized if len(w) and (w[0]=='#') ]
            for ht in hashtags:
                toks = hashtag.split_hashtag(ht)
                for tok in toks:
                    features[('hashtag-tok',tok.lower())] = 1
        '''
 

        # Feature: Punctuation counts
        text = ' '.join(phrase)
        for c in '!?':
            features['%s-count'  %c] = text.count(c)


        # Result: Slightly better
        features['phrase_length'] = len(phrase) / 4


        if enabled_modules['ukb_wsd'] and enabled_modules['ark_tweet']:
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
        #normalized = utilities.normalize_phrase_TaskB(phrase)
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

