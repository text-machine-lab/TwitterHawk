#-------------------------------------------------------------------------------
# Name:        taskb_lexicon_features.py
#
# Purpose:     Lexicon features
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import os,sys
import string
from collections import defaultdict


# Add common-lib code to system path
sources = os.getenv('BISCUIT_DIR')
if sources not in sys.path: sys.path.append(sources)


# If enabled, build all lexicons
from common_lib.read_config import enabled_modules
if enabled_modules['lexicons']:
    from common_lib.common_lexicons.lexicons import lexHTS
    from common_lib.common_lexicons.lexicons import lexS140
    from common_lib.common_lexicons.lexicons import lexSubj
    from common_lib.common_lexicons.lexicons import lexOpi
    from common_lib.common_lexicons.lexicons import lexEmo
    from common_lib.common_lexicons.lexicons import lexAff
    from common_lib.common_lexicons.lexicons import lexClus
    from common_lib.common_lexicons.lexicons import lexInq

from common_lib.common_features.utilities import normalize_phrase_TaskA



def light_normalize(sentence, begin, end, ark_tweet):

    # Normalize phrase
    normalized = normalize_phrase_TaskA(sentence, ark_tweet, stem=False)

    # Get given phrase
    phrase = [ w for words in normalized[begin:end] for w in words ]

    return [  word.lower()  for  word  in  phrase  ]



def heavy_normalize(phrase):
    return phrase



# Useful helper functions
def k_most_influential(lst, k):
    """
        return reverse sorted length-k list with largest abs values from lst
        ex. k_most_influential([1,5,-10,3,7,-6], 2)  -->  [-10,7,6]
    """
    return sorted(lst, key=abs, reverse=True)[:k]


def average(lst):
    return sum(lst) / (len(lst) + 1e-5)


def is_positive(score):
    return score > 0


def scores_to_features(scores, lexName, featName):
    features = {}

    if len(scores) == 0: return {}

    # Average scores
    features[('avg_score', (lexName,featName))] = average(scores)

    # List of positive scores
    pos_scores = filter(is_positive, scores)

    # num_of_positive, max_score, last_positive
    features[('positive_count', (lexName,featName))]  =  len(pos_scores)
    features[('max'           , (lexName,featName))]  =  max(    scores)
    if len(pos_scores):
        features[('last_posit', (lexName,featName))]  =   pos_scores[-1]

    return features




def opinion_lexicon_features(phrase):

    features = {}

    # TODO - Maybe do % positive, rather than num_positive
    # Count number of positive, negative, and neutral labels there are
    Opi_sentiments = defaultdict(lambda:0)
    for word in phrase:
        label = lexOpi.lookup(word)
        Opi_sentiments[label] += 1
    for sentiment,count in Opi_sentiments.items():
        if sentiment ==        '': continue
        features[ ('Opi-count', sentiment) ] = count

    return features




def subjectivity_lexicon_features(phrase):

    features = {}

    # FIXME - MUST disambiguate POS
    # Feature Subjectivity Classification
    #print '\n\n'
    #print phrase
    Subj_sentiments = defaultdict(lambda:0)
    for word in phrase:
        entry = lexSubj.lookup(word)
        #print '\t', word, '\t\t\t', entry
        if entry.prior != '':
            label = (entry.type, entry.prior)   # ex. ('strongsub','positive')
            Subj_sentiments[label] += 1
    for sentiment,count in Subj_sentiments.items():
        #print 'feat: ', 'Subj-%s-%s_count' % sentiment, '\t\t', count
        features[ ('Subj-%s-%s_count', sentiment) ] = count

    return features



def emotion_lexicon_features(phrase):

    # Emotion Scores
    lexEmo_uni_scores = defaultdict(lambda:[])
    for w in phrase:
        senti = lexEmo.lookup(w)
        lexEmo_uni_scores[senti[0]].append( senti[1] )

    # Get features for each kind of emotion
    features = {}
    for e,scores in lexEmo_uni_scores.items():
        emotion_feats = scores_to_features(scores, 'Emo', e)
        features.update(emotion_feats)

    return features



def affin_lexicon_features(phrase):
    # Add Affin Features
    scores = []
    for word in phrase:
        score = lexAff.score(word)
        if score != None: scores.append(score)
    return scores_to_features(scores, 'Affin', 'score')



def brown_cluster_features(phrase):

    features = {}

    # Add Brown Cluster Features
    lastCluster = None
    clusterDict = lexClus.getBlankDict()
    for word in phrase:
        wordCluster = lexClus.getCluster(word)
        if wordCluster != None:
            if ('Cluster-count',wordCluster) in features.keys():
                features[('Cluster-count',wordCluster)] += 1
            else:
                features[('Cluster-count',wordCluster)] = 1
            #clusterDict[wordCluster] += 1
            lastCluster = wordCluster
    for key in clusterDict:
        if clusterDict[key] > 0:
            features[('Cluster-count',key)] = clusterDict[key]
    if lastCluster != None:
        features[('Cluster-last',lastCluster)] = 1

    return features




def general_inquirer_features(phrase):

    features = {}

    #Add General Inquirer Features
    lastTags = None
    tagDict = defaultdict(lambda:0)
    for word in phrase:
        #print word
        wordTags = lexInq.getTags(word)
        #print 'wordTags: ', wordTags
        if wordTags != None:
            for tag in wordTags:
                #print '\t', tag
                tagDict[tag] += 1
            lastTags = wordTags
        #print
    #print 'tagDict: ', tagDict
    for key in tagDict:
        if tagDict[key] > 0:
            features[('Tag-count',key)] = tagDict[key]
    if lastTags != None:
        for tag in lastTags:
            features[('Tag-last',tag)] = 1

    return features




def sentiment_lexicon_features(phrase, lexName, lex):

    # Unigram features
    def sentiment_lexicon_unigram_features():
        # Build unigram scores
        uni_scores  = [ lex.lookupUnigram(w).score  for  w  in  phrase  ]

        # Get features for unigrams
        return scores_to_features(uni_scores, lexName, 'unigram')


    # Bigram features
    def sentiment_lexicon__bigram_features():
        # Build bigram scores
        bi_scores  = []
        for i in range(len(phrase) - 1):
            bigram = (phrase[i], phrase[i+1])
            bi_scores.append( lex.lookupBigram(bigram).score )

        # Get features for bigrams
        return scores_to_features(bi_scores, lexName, 'bigram')


    def sentiment_lexicon___pairs_features():
        # Build pair scores
        pairs = []
        for i in range(len(phrase) - 1):
            unigram = phrase[i]
            rest    = phrase[i+1:]

            # uni-uni
            for w in rest:
                pairs.append( (unigram,w) )

            # uni-bi
            for j in range(len(rest)-1):
                bi = tuple(rest[j:j+2])
                pairs.append( (unigram,bi) )

            # bi-bi
            bigram = tuple(phrase[i:i+2])
            rest   = phrase[i+2:]
            for j in range(len(rest)-1):
                bi = tuple(rest[j:j+2])
                pairs.append( (bigram,bi) )
        pair_scores  = [  lex.lookupPair(p).score  for  p  in  pairs  ]

        # Get features for pairs
        return scores_to_features(pair_scores, lexName, 'pairs')


    # Call helper functions and combine results
    features = {}

    features.update(sentiment_lexicon_unigram_features())
    features.update(sentiment_lexicon__bigram_features())
    features.update(sentiment_lexicon___pairs_features())

    return features




def lexicon_features(sentence, begin, end, ark_tweet=None):

    """
    lexicon_features()
    @return      A feature dictionary.
    """

    features = {}

    # Light normalization
    phrase = light_normalize(sentence, begin, end, ark_tweet)

    # Aplly all twitter-specfic lexicons
    features.update(   opinion_lexicon_features(phrase)                  )
    features.update( sentiment_lexicon_features(phrase,  'HTS', lexHTS ) )
    features.update( sentiment_lexicon_features(phrase, 'S140', lexS140) )
    features.update(   emotion_lexicon_features(phrase)                  )
    features.update(     brown_cluster_features(phrase)                  )


    # Heavier normalization (ex. spell correct & hashtag split)
    #phrase = heavy_normalize(sentence)

    # Apply all general-purpose lexicons
    features.update( subjectivity_lexicon_features(phrase)                  )
    features.update(        affin_lexicon_features(phrase)                  )
    features.update(     general_inquirer_features(phrase)                  )

    #if features:
    #    print phrase
    #    print features
    #    print '\n\n'

    return features

