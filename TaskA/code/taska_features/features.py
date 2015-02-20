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
import spell


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



# Common spelling abbreviations and mistakes
common = {}
abbrevs = os.path.join('/data1/nlp-data/twitter/tools/spell/abbrv.txt')
with open(abbrevs,'r') as f:
    for line in f.readlines():
        if line == '\n': continue
        abbrev,full = tuple(line.strip('\n').split(' || '))
        common[abbrev] = full



class FeaturesWrapper:

    def __init__(self):

        # Tag/Chunk data with ark_tweet_nlp
        if enabled_modules['ark_tweet']:
            self.ark_tweet = ark_tweet.ArkTweetNLP()
        else:
            self.ark_tweet = None

        # Spelling correction
        self.speller = spell.SpellChecker()

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
        sentence = [ unicode(t.decode('utf-8')) for t in tweet_repr[2] ]
        phrase   = sentence[begin:end+1]


        # Feature Dictionary
        features = {}


        # Normalize all text (tokenizer, stem, etc)
        corrected = sentence
        normalized = utilities.normalize_phrase_TaskA(corrected,ark_tweet=self.ark_tweet)
        flat_normed = [ w for words in normalized for w in words ]


        # Feature: unedited term unigrams
        for tok in phrase:
            if tok == '': continue
            if tok in utilities.stop_words:      continue
            features[('unedited-uni-tok',tok)] = 1


        # Term unigrams
        for tok in normalized[begin:end+1]:
            for word in tok:
                if word == '': continue
                if word[0] == '#': continue
                base  = word if (word[-4:]!='_neg') else word[:-4] 
                if base in utilities.stop_words:      continue

                if base.lower() in common:
                    toks = common[base.lower()].split()
                else:
                    toks = [base]

                for t in toks:
                    w = st.stem(t)
                    if word[-4:] == '_neg':
                        w += '_neg'

                    weight = 1
                    if utilities.is_elongated_word(base): weight += 1

                    features[('stemmed_term_unigram', w)] = weight


        # Unigram context window
        window = 3
        prefix_start = max(begin-window, 0)
        context = sentence[prefix_start:end+1+window]

        norm_context = [ w for t in normalized[begin:end+1] for w in t ]

        prefix_terms = []
        for w in reversed([w for t in normalized[prefix_start:begin]for w in t]):
            if w == '': break
            prefix_terms.append(w)
        norm_context = list(reversed(prefix_terms)) + norm_context
 
        suffix_terms = []
        for w in [ w for t in normalized[end+1:end+1+window] for w in t ]:
            if w == '': break
            suffix_terms.append(w)
        norm_context = norm_context + suffix_terms


        # Feature: Unigram context
        # Leading
        for word in norm_context:
            if word == '': continue
            w  = word if (word[-4:]!='_neg') else word[:-4] 
            if w in utilities.stop_words:      continue
            w = st.stem(self.speller.correct_spelling([w])[0])
            if word[-4:] == '_neg':
                w += '_neg'
            features[('leading_unigram', w)] = 1

        '''
        print sentence
        print phrase
        for k,v in features.items():
            print '\t', k, '\t', v
        return features
        '''

        # Feature: Lexicon Features
        if enabled_modules['lexicons']:
            #print '\n\n\n'
            #print 'LEX FEATS: ', sentence
            #print begin, end
            # Phrase in question
            lex_feats = lexicon_features(sentence,begin,end+1,ark_tweet=self.ark_tweet)
            context_feats = lexicon_features(sentence,prefix_start,end+1+window,ark_tweet=self.ark_tweet)
            features.update(lex_feats)

            '''
            # Leading context
            prev_lex_feats = lexicon_features(sentence,prefix_start,begin, ark_tweet=self.ark_tweet)
            prev_lex_feats = {('prev-'+k[0],k[1]):v for k,v in prev_lex_feats.items()}
            features.update(prev_lex_feats)

            # Trailing context
            next_lex_feats = lexicon_features(sentence,end+1,end+1+window, ark_tweet=self.ark_tweet)
            next_lex_feats = {('next-'+k[0],k[1]):v for k,v in next_lex_feats.items()}
            features.update(next_lex_feats)
            '''


            #print phrase
            #for k,v in lex_feats.items():
            #    print '\t', k, '\t', v
            #print

            #print lex_feats
            #print prev_lex_feats
            #print next_lex_feats


        # Feature: Split hashtag
        if enabled_modules['hashtag']:
            hashtags = [ w for w in context if len(w) and (w[0]=='#') ]
            for ht in hashtags:
                toks = hashtag.split_hashtag(ht)
                for tok in utilities.normalize_phrase_TaskB(toks):
                    w = tok if tok[-4:]!='_neg' else tok[:-4]
                    stemmed = st.stem(w)
                    if tok[-4:] == '_neg': stemmed += '_neg'
                    if len(w) < 2: continue
                    if w in utilities.stop_words: continue
                    features[('stemmed_term_unigram',stemmed)] = 1


        #print
        #print sentence
        #print begin
        #print end
        #print phrase

        # Feature: Prefixes and Suffixes
        n = [2,3,4]
        for i,words in enumerate(normalized[begin:end+1]):
            for word in words:
                if len(word) < 2: continue
                for j in n:
                    if word[-4:] == '_neg': word = word[:-4]

                    prefix = word[:j ]
                    suffix = word[-j:]

                    #print '\tprefix: ', prefix
                    #print '\tsuffix: ', suffix
                    features[ ('prefix',prefix) ] = 1
                    features[ ('suffix',suffix) ] = 1


        # Features: Special forms
        if any([ utilities.is_url(w) for w in phrase]):
            features[ ('contains_url',None) ] = 1
        if any([ w and w[0]=='@'     for w in phrase]):
            features[ ('contains_@'  ,None) ] = 1
        if any([ w and w[0] == '#'   for w in phrase]):
            features[ ('contains_#'  ,None) ] = 1



        # Features: Misc position data
        features['first_unigram'] = sentence[begin]
        features[ 'last_unigram'] = sentence[  end]
        features['phrase_length'] = len(phrase) / 2.0
        features['is_first'] = (begin == 0)
        features['is_last'] = (end == len(sentence)-1)


        # Feature: Whether every word is a stop word
        if all([ tok in utilities.stop_words for tok in phrase]):
            #print phrase
            features[ ('all_stopwords',None) ] = 1


        # Feature: All Caps? (boolean)
        if re.search('^[^a-z]*[A-Z][A-Z][^a-z]$',''.join(phrase)):
            features[ ('all_caps',None) ] = 1


        # Feature: All Punctuation?
        if re.search('^[^a-zA-Z0-9]+$',''.join(phrase)):
            features[ ('all_punct',None) ] = 1


        # Feature: Emoticon Counts
        elabels = defaultdict(lambda:0)
        for word in norm_context:
            elabel = emoticons.emoticon_type(word)
            if elabel:
                elabels[elabel] += 1
        for k,v in elabels.items():
            featname = k + '-emoticon'
            features[featname] = v


        # Feature: Punctuation counts
        punct = {'!':0, '?':0, '.':0}
        for c in ''.join(context):
            if c in punct: punct[c] += 1
        for k,v in punct.items():
            featname = k + '-count'
            features[featname] = v


        # Features: character streaks
        text = ''.join(phrase)

        #  !-streak
        matches = re.findall('!+',text)
        if matches:
            features['!-streak'] = max([len(w) for w in matches])

        #  ?-streak
        matches = re.findall('\\?+',text)
        if matches:
            features['?-streak'] = max([len(w) for w in matches])

        # ?!-streak
        matches = re.findall('[!\\?]+',text)
        if matches:
            features['?!-streak'] = max([len(w) for w in matches])


        # Feature: Contains elongated long word? (boolean)
        contains_elongated_word = False
        for word in phrase:
            if utilities.is_elongated_word(word):
                contains_elongated_word = True
        if contains_elongated_word:
            features[ ('contains_elongated_word',None) ] = 1


        # Feature: Contains long word? (boolean)
        long_word_threshold = 10
        contains_long_word = False
        for words in normalized[begin:end+1]:
            for word in words:
                if word[-4:]=='_neg': word = word[:-4]
                word = spell.remove_duplicates(word)
                if len(word) and word[0]=='#': continue
                word = word.strip(string.punctuation)
                if len(word) > long_word_threshold:
                    contains_long_word = True
        if contains_long_word:
            features[ ('contains_long_word',None) ] = 1



        return features

