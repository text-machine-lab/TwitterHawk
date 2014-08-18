#-------------------------------------------------------------------------------
# Name:        features.py
#
# Purpose:     Extract features from tweets
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import emoticons
import utilities
from lexicons.lexicons import lexHTS, lexS140, lexOpi, lexSubj, lexEmo

from collections import defaultdict



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
    normalized = utilities.normalize_phrase(phrase)
    for word in normalized:
        features[('term_unigram', word)] = 1


    return features


    # Feature: Lexicon Features
    feats = lexicon_features(phrase)
    features.update(feats)


    return features



    # Decreases normalized unigrams + lexicon
    # Full string
    features['phrase'] = ' '.join(phrase)


    # Decreases normalized unigrams + lexicons
    # Unigram context window
    window = 4

    # Leading unigrams
    prefix_start = begin-window  if  (begin-window > 0)  else  0
    prefix = utilities.normalize_phrase(sentence[prefix_start:begin])
    for word in prefix:
        features[('leading_unigram', word)] = 1


    # Trailing unigrams
    suffix = utilities.normalize_phrase(sentence[end+1:end+1+window])
    for word in suffix:
        features[('trailing_unigram', word)] = 1


    '''
    #print sentence
    #print phrase                      , ' -> ', normalized
    #print sentence[prefix_start:begin], ' -> ', prefix
    #print sentence[end+1:end+1+window], ' -> ', suffix
    #print ''
    '''



    # These don't do much
    features['first_unigram'] = sentence[begin]
    features[ 'last_unigram'] = sentence[  end]


    features['phrase_length'] = len(phrase)




    if len(normalized) == 0:
        features['all_stopwords'] = 1



    #return features



    # Feature: Prefixes and Suffixes
    n = [2,3]
    for i,word in enumerate(normalized):
        for j in n:
            if word[-4:] == '_neg': word = word[:-3]

            prefix = word[:j]
            suffix = word[-1-j+1:]

            features[ ('prefix',prefix) ] = 1
            features[ ('suffix',suffix) ] = 1





    # Note: Bigrams assume order, but 'normalized' is basically a set
    # Feature: Bigrams
    for i in range(len(phrase) - 1):
        ngram = ' '.join(normalized[i:i+2])
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
        if utilities.isElongatedWord(word):
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
        if utilities.isElongatedPunctuation(word):
            contains_elongated_punc = True
            break
    features[ ('contains_elongated_punc',contains_elongated_punc) ] = 1


    #print tweet_repr
    #for i,w in enumerate(sentence):
    #    print '\t', i, ' ', w
    #print features
    #print '---\n'

    return features





def lexicon_features(phrase):

    """
    features_for_word()

    @param word. A word from a tweet
    @return      A feature dictionary
    """

    # Slight normalization
    phrase = [  w.lower()  for  w  in  phrase  ]
    phrase = utilities.stripPunctuation(phrase)


    features = {}


    '''
    # Features: Opinion & Subjectivity Classifications
    for word in phrase:
        lexOpi_label = lexOpi.lookup(word)
        features[ ('lexOpi_unigram',lexOpi_label) ] = 1

        lexSubj_label = lexSubj.lookup(word).prior
        features[ ('lexSubj_unigram',lexSubj_label) ] = 1
    '''


    # Features: Sentiment Scores
    lexHTS_uni_scores  = []
    lexS140_uni_scores = []
    for word in phrase:
        lexHTS_uni_scores.append(   lexHTS.lookupUnigram(word).score )
        lexS140_uni_scores.append( lexS140.lookupUnigram(word).score )


    print '\tphrase: ', phrase
    print '\tHTS :   ', lexHTS_uni_scores
    print '\tS140:   ', lexS140_uni_scores
    print


    polarities = polarity_count('HTS', lexHTS_uni_scores)

    print polarities
    print

    return features


    '''
    # Three most influential sentiments
    inf_uni_HTS = sorted(lexHTS_uni_scores,key=abs,reverse=True)
    for i,score in enumerate(inf_uni_HTS[:3]):
        featname = 'lexHTS_unigram-influential-%d' % i
        features[featname] = score

    inf_uni_S140 = sorted(lexS140_uni_scores,key=abs,reverse=True)
    for i,score in enumerate(inf_uni_S140[:3]):
        featname = 'lexS140_unigram-influential-%d' % i
        features[featname] = score
    '''

    # Features: Emotion Scores
    lexEmo_uni_scores = []
    for word in phrase:
        lexEmo_uni_scores.append(lexEmo.lookup(word))

    # Three most influential emotions
    inf_uni_Emo = sorted(lexEmo_uni_scores,key=lambda t:t[1])
    for i,tup in enumerate(inf_uni_Emo[-3:]):
        featname = ('lexEmo_unigram-influential', tup[0])
        score = tup[1]
        features[featname] = score


    '''
    # Average scores
    features['avg_HTS' ] = max(inf_HTS ) / (sum(inf_HTS ) + 1e-5)

    features['avg_S140'] = max(inf_S140) / (sum(inf_S140) + 1 e-5)


    emo_scores = defaultdict(lambda:[])
    for e,score in reversed(inf_Emo):
        emo_scores[e].append(score)
    for e,scores in emo_scores.items():
        featname = 'avg_Emo-' + e
        features[featname] = max(scores ) / (sum(scores ) + 1e-5)
    '''




    # Features; Bigram Senitment Scores
    lexHTS_bi_scores  = []
    lexS140_bi_scores = []
    for i in range(len(phrase) - 1):
        bigram = phrase[i], phrase[i+1]
        lexHTS_bi_scores.append(   lexHTS.lookupUnigram(bigram).score )
        lexS140_bi_scores.append( lexS140.lookupUnigram(bigram).score )

    inf_bi_HTS = sorted(lexHTS_bi_scores,key=abs,reverse=True)
    for i,score in enumerate(inf_bi_HTS):
        featname = 'lexHTS_bigram-influential-%d' % i
        features[featname] = score

    inf_bi_S140 = sorted(lexS140_bi_scores,key=abs,reverse=True)
    for i,score in enumerate(inf_bi_S140):
        featname = 'lexS140_bigram-influential-%d' % i
        features[featname] = score


    '''
    # Average scores
    #print inf_HTS
    features['avg_bigram_HTS' ] = max(inf_HTS ) / (sum(inf_HTS ) + 1e-5)
    features['avg_bigram_S140'] = max(inf_S140) / (sum(inf_S140) + 1e-5)
    '''


    return features



def polarity_count(lex_name, scores):

    polarities = {'positive':0, 'negative':0, 'neutral':0}
    threshhold = .2

    # Count number of words for each polarity
    for score in scores:
        if   score < -1 * threshhold:
            key = 'negative'
        elif score >      threshhold:
            key = 'positive'
        else:
            key = 'neutral'
        polarities[key] += 1


    # Prepend lexicon name to scores
    polarities = {  lex_name+'-'+k : v   for   k,v   in   polarities.items()   }


    return polarities