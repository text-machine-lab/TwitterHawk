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
    from common_lib.common_lexicons.lexicons import lexOpi
    from common_lib.common_lexicons.lexicons import lexSubj
    from common_lib.common_lexicons.lexicons import lexEmo
    from common_lib.common_lexicons.lexicons import lexAff
    from common_lib.common_lexicons.lexicons import lexClus
    from common_lib.common_lexicons.lexicons import lexInq

def light_normalize(phrase):
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


def max0(lst):
    """
        max of a list, but has default value of 0
    """
    if not lst: return 0
    return max(lst)


def average(lst): 
    return sum(lst) / (len(lst) + 1e-5)


def is_positive(score): 
    return score > 0




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
        features[ 'Opi-%s_count' % sentiment ] = count

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
        features[ 'Subj-%s-%s_count' % sentiment ] = count

    return features



def emotion_lexicon_features(phrase):

    features = {}

    # Emotion Scores
    lexEmo_uni_scores = defaultdict(lambda:[])
    for w in phrase:
        senti = lexEmo.lookup(w)
        lexEmo_uni_scores[senti[0]].append( senti[1] )

    # for each emotion: avg_score, num_positive, max_positive, last_positive
    feats = {}
    for e,scores in lexEmo_uni_scores.items():
        pos  = filter(is_positive, scores)
        features[ 'Emo-uni-%s-avg'            % e ] = average(scores)
        features[ 'Emo-uni-%s-positive_count' % e ] =  len(pos)
        features[ 'Emo-uni-%s-max'            % e ] = max0(pos)
        if len(pos):
            features[ 'Emo-uni-%s-last_pos' % e ] = pos[-1]

    # for each emotion: 3 most influential scores
    for e,scores in lexEmo_uni_scores.items():
        inf_Emo = k_most_influential(scores, 3)
        for i,score in enumerate(inf_Emo):
            features[ 'Emo-%s-unigram-influential-%d' % (e,i) ] = score
        features[('Emo-count',e)] = len(scores)

    return features



def affin_lexicon_features(phrase):

    features = {}

    #Add Affin Features
    affTotal = 0
    affDict = {n:0 for n in range(-5,6)}
    affLast = 0
    for word in phrase:
        affScore = lexAff.score(word)
        if affScore != None:
            affTotal += affScore
            affDict[affScore] += 1
            affLast = affScore
    features['Affin-Sum'] = affTotal
    for key in affDict:
        features[('Aff-score',key)] = affDict[key]
    features['Aff-last'] = affLast

    return features



def brown_cluster_features(phrase):

    features = {}

    #Add Brown Cluster Features
    lastCLuster = None
    #clusterDict = lexClus.getBlankDict()
    for word in phrase:
        wordCluster = lexClus.getCluster(word)
        if wordCluster != None:
            if ('Cluster-count',wordCluster) in features.keys():
                features[('Cluster-count',wordCluster)] += 1
            else:
                features[('Cluster-count',wordCluster)] = 1
            #clusterDict[wordCluster] += 1
            lastCluster = wordCluster
    #for key in clusterDict:
    #    features[('Cluster-count',key)] = clusterDict[key]
    if lastCluster != None:
        features[('Cluster-last',lastCluster)] = 1

    return features




def general_inquirer_features(phrase):

    features = {}

    #Add General Inquirer Features
    lastTags = None
    #tagDict = lexInq.getBlankDict()
    for word in phrase:
        wordTags = lexInq.getTags(word)
        if wordTags != None:
            for tag in wordtags:
                if ('Tag-count',tag) in features.keys():
                    features[('Tag-count',tag)] += 1
                else:
                    features[('Tag-count',tag)] = 1
                #tagDict[tag] += 1
            lastTags = wordTags
    #for key in tagDict:
    #    features[('Tag-count',key)] = tagDict[key]
    if lastTags != None:
        for tag in lastTags:
            features[('Tag-last',tag)] = 1

    return features




def sentiment_lexicon_features(phrase, lexName, lex):

    # FIXME / TODO - Follow paper very closely
    def scores_to_features(scores, featName):
        features = {}

        # Three most influential sentiments (AKA scores with largest abs value)
        influential = k_most_influential(scores, 3)

        # Add influential scores to feature dict
        for i,score in enumerate(influential):
            features[  '%s-%s-influential-%d' % (lexName,featName,i) ] = score

        # Average scores
        features['%s-%s-avg_score' % (lexName,featName)] = average(scores)

        # List of positive scores
        pos_scores = filter(is_positive, scores)

        # num_of_positive, max_positive, last_positive
        features['%s-%s-positive_count' % (lexName,featName)]  =  len(pos_scores)
        features['%s-%s-max'            % (lexName,featName)]  = max0(pos_scores)
        if len(pos_scores):
            features['%s-%s-last_pos'   % (lexName,featName)]  =   pos_scores[-1]

        return features


    # Unigram features
    def sentiment_lexicon_unigram_features():
        uni_scores  = [ lex.lookupUnigram(w).score  for  w  in  phrase  ]
        return scores_to_features(uni_scores, 'unigram')

    # Bigram features
    def sentiment_lexicon__bigram_features():
        # Build bigram scores
        bi_scores  = []
        for i in range(len(phrase) - 1):
            bigram = (phrase[i], phrase[i+1])
            bi_scores.append( lex.lookupBigram(bigram).score )
        return scores_to_features(bi_scores, 'bigram')


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

        return scores_to_features(pair_scores, 'pairs')


    # Call helper functions and combine results
    features = {}

    features.update(sentiment_lexicon_unigram_features())
    features.update(sentiment_lexicon__bigram_features())
    features.update(sentiment_lexicon___pairs_features())

    return features




def lexicon_features(phrase):

    """
    lexicon_features()

    @param word. A split list of words from a tweet.
    @return      A feature dictionary.
    """

    features = {}


    # Slight normalization
    phrase = light_normalize(phrase)

    # Aplly all twitter-specfic lexicons
    features.update(   opinion_lexicon_features(phrase)                  )
    features.update( sentiment_lexicon_features(phrase,  'HTS', lexHTS ) )
    features.update( sentiment_lexicon_features(phrase, 'S140', lexS140) )
    #features.update(   emotion_lexicon_features(phrase)                  )
    features.update(     brown_cluster_features(phrase)                  )


    # Heavier normalization (ex. spell correct & hashtag split)
    phrase = heavy_normalize(phrase)

    # Apply all general-purpose lexicons
    features.update( subjectivity_lexicon_features(phrase)                  )
    #features.update(        affin_lexicon_features(phrase)                  )
    #features.update(  general_inquirer_features(phrase)                  )


    return features

