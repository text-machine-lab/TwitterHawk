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


from taska_lexicon_features import lexicon_features


# Add common-lib code to system path
sources = os.path.join(os.getenv('BISCUIT_DIR'))
if sources not in sys.path: sys.path.append(sources)

# All from common-lib
from common_lib.read_config     import enabled_modules
from common_lib.common_features import utilities
from common_lib.common_lexicons import emoticons


def features_for_tweet(tweet_repr):

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


    # Term unigrams
    normalized = utilities.normalize_phrase_TaskA(sentence, stem=True)
    for tok in normalized[begin:end+1]:
        for word in tok:
            features[('term_unigram', word)] = 1


    # Feature: Lexicon Features
    if enabled_modules['lexicons']:
        lex_feats = lexicon_features(phrase)
        features.update(lex_feats)


    # Unigram context window
    window = 3
    prefix_start = max(begin-window, 0)


    '''
    # Lexicon lookup for context window
    # Leading context
    prev_lex_feats = lexicon_features(sentence[prefix_start:begin])
    prev_lex_feats = {(('prev-'+k[0],k[1]),v) for k,v in prev_lex_feats.items()}
    features.update(prev_lex_feats)

    # Trailing context
    next_lex_feats = lexicon_features(sentence[end+1:end+1+window])
    next_lex_feats = {(('next-'+k[0],k[1]),v) for k,v in next_lex_feats.items()}
    features.update(next_lex_feats)
    '''

    '''
    # Leading unigrams
    for tok in normalized[prefix_start:begin]:
        for word in tok:
            features[('leading_unigram', word)] = 1


    # Trailing unigrams
    for tok in normalized[end+1:end+1+window]:
        for word in tok:
            features[('trailing_unigram', word)] = 1
    '''


    # Print out normalization
    #for w,t in zip(sentence,normalized):
    #    print w, '\t', t
    #print

    #print sentence
    #print normalized[prefix_start:begin]
    #print normalized[begin:end+1]
    #print normalized[end+1:end+1+window]
    #print


    #return features



    # Full string
    features['phrase'] = ' '.join(phrase)


    '''
    #print sentence
    #print phrase                      , ' -> ', normalized
    #print sentence[prefix_start:begin], ' -> ', prefix
    #print sentence[end+1:end+1+window], ' -> ', suffix
    #print ''
    '''

    #return features


    # These don't do much
    features['first_unigram'] = sentence[begin]
    features[ 'last_unigram'] = sentence[  end]

    features['phrase_length'] = len(phrase)



    if all([ (len(tok) == 0) for tok in normalized[begin:end+1]]):
        print sentence
        print begin, end
        print 'ALL stopwords: ', phrase
        print
        features['all_stopwords'] = 1



    #return features



    # Feature: Prefixes and Suffixes
    n = [2,3]
    for i,tok in enumerate(normalized):
        for j in n:
            for word in tok:
                if word[-4:] == '_neg': word = word[:-3]

                prefix = word[:j ]
                suffix = word[-j:]

                features[ ('prefix',prefix) ] = 1
                features[ ('suffix',suffix) ] = 1



    return features


    # Feature: Bigrams
    for i in range(len(phrase) - 1):
        ngram = ' '.join(phrase[i:i+2])
        features[ ('bigram',ngram) ] = 1




    # Rating: Not great
    # Feature: All Caps? (boolean)
    is_all_caps = True
    for word in phrase:
        if word != word.upper():
            is_all_caps = False
            break
    features[ ('all_caps',is_all_caps) ] = 1




    # Rating: Might be good (unsure) bad
    # Feature: Contains elongated long word? (boolean)
    contains_elongated_word = False
    for word in phrase:
        if utilities.is_elongated_word(word):
            contains_elongated_word = True
            break
    features[ ('contains_elongated_word',contains_elongated_word) ] = 1




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



    # Not useful
    # Feature: All Capitalization? (boolean)
    is_all_capitalization = True
    for word in phrase:
        if not word: continue
        if word[0].islower():
            is_all_capitalization = False
            break
    features[ ('all_capitalization',is_all_capitalization) ] = 1




    # Rating: Bad :(
    # Feature: Punctuation counts
    punct = {'!':0, '?':0}
    for c in ''.join(phrase):
        if c in punct: punct[c] += 1
    for k,v in punct.items():
        featname = k + '-count'
        features[featname]= v



    # Feature: Contains long word? (boolean)
    long_word_threshold = 8
    contains_long_word = False
    for word in phrase:
        if len(word) > long_word_threshold:
            contains_long_word = True
            break
    features[ ('contains_long_word',contains_long_word) ] = 1



    # Feature: Contains elongated long punctuation? (boolean)
    contains_elongated_punc = False
    for word in phrase:
        if utilities.is_elongated_punctuation(word):
            contains_elongated_punc = True
            break
    features[ ('contains_elongated_punc',contains_elongated_punc) ] = 1


    #print tweet_repr
    #for i,w in enumerate(sentence):
    #    print '\t', i, ' ', w
    #print features
    #print '---\n'

    return features

