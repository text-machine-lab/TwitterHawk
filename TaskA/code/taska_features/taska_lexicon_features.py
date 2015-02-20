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
    from common_lib.common_lexicons.lexicons import lexOpi
    from common_lib.common_lexicons.lexicons import lexSubj
    from common_lib.common_lexicons.lexicons import lexEmo
    from common_lib.common_lexicons.lexicons import lexAff
    from common_lib.common_lexicons.lexicons import lexHTS
    from common_lib.common_lexicons.lexicons import lexS140
    from common_lib.common_lexicons.lexicons import lexInq

    #from common_lib.common_lexicons.lexicons import lexClus

from common_lib.common_features.utilities import normalize_phrase_TaskA, is_elongated_word




# Common spelling abbreviations and mistakes
common = {}
abbrevs = os.path.join('/data1/nlp-data/twitter/tools/spell/abbrv.txt')
with open(abbrevs,'r') as f:
    for line in f.readlines():
        if line == '\n': continue
        abbrev,full = tuple(line.strip('\n').split(' || '))
        common[abbrev] = full


def light_normalize(sentence, begin, end, ark_tweet):

    # Normalize phrase
    normalized = normalize_phrase_TaskA(sentence, ark_tweet)

    # Get given phrase
    phrase = [ w.lower() for words in normalized[begin:end] for w in words ]

    # Common spelling mistakes
    retVal = []
    for t in phrase:
        if t == '': continue

        negated = ('_neg' in t)
        if negated: t = t[:-4]

        key = t.strip(string.punctuation)
        if key in common:
            abbrv = common[key].split()
            if negated: abbrv = [ w+'_neg' for w in abbrv ]
            retVal += abbrv
        else:
            if negated: key += '_neg'
            retVal.append(key)
            if t[0] == '#': retVal.append(t)
    phrase = retVal

    return phrase



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

    #for i,s in enumerate(k_most_influential(scores,3)):
    #    features[('%d-most-influential'%i,(lexName,featName))] = s

    if len(pos_scores):
        features[('last_posit', (lexName,featName))]  =   pos_scores[-1]

    return features


def context_lookup(lookup_fcn, w):
    negated = -1 if (w[-4:] == '_neg') else 1
    if w[-4:] == '_neg': w = w[:-4]
    score = lookup_fcn(w) * negated
    return score



def opinion_lexicon_features(phrase):

    features = {}

    # Count number of positive, negative, and neutral labels there are
    Opi_sentiments = defaultdict(lambda:0)
    for word in phrase:
        negated = ('_neg' in word)
        if negated: word = word[:-4]
        label = lexOpi.lookup(word)
        if label != 'neutral':
            if negated:
                if label == 'positive':
                    label = 'negative'
                else:
                    label = 'positive'
            Opi_sentiments[label] += 1

    for sentiment,count in Opi_sentiments.items():
        if sentiment == '': continue
        features[ ('Opi-count', sentiment) ] = count

    return features




def subjectivity_lexicon_features(phrase):

    features = {}

    # FIXME - MUST disambiguate POS
    # Feature Subjectivity Classification
    Subj_sentiments = defaultdict(lambda:0)
    for word in phrase:
        negated = ('_neg' in word)
        if negated: word = word[:-4]

        entry = lexSubj.lookup(word)
        if entry.prior != '':
            label = (entry.type, entry.prior)   # ex. ('strongsub','positive')

            if negated:
                if   label[1] == 'positive':
                    label = ('weaksubj','negative')
                elif label[1] == 'negative':
                    label = ('weaksubj','positive')

            Subj_sentiments[label] += 1

    for sentiment,count in Subj_sentiments.items():
        features[ ('Subj-%s-%s_count' % sentiment) ] = count

    return features



def emotion_lexicon_features(phrase):

    # Emotion Scores
    lexEmo_uni_scores = defaultdict(lambda:[])
    for w in phrase:
        context = (w[-4:] == '_neg')
        if context: w = w[:-4]
        senti = lexEmo.lookup(w)
        if context:
            score = -senti[1]
        else:
            score =  senti[1]

        lexEmo_uni_scores[senti[0]].append( score )

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
        negated = ('_neg' in word)
        if negated: word = word[:-4]

        score = lexAff.score(word)
        if score != None:
            if negated: score = 0
            scores.append(score)

    return scores_to_features(scores, 'Affin', 'score')



def brown_cluster_features(phrase):

    features = defaultdict(lambda:0)

    # Add Brown Cluster Features
    lastCluster = None
    clusters = []
    for word in phrase:
        context = (word[-4:] == '_neg')
        if context: word = word[:-4]
        wordCluster = lexClus.getCluster(word)
        clusters.append(wordCluster)
        if wordCluster != None:
            features[('Cluster-count',(context,wordCluster))] += 1
            lastCluster = wordCluster
    if lastCluster != None:
        features[('Cluster-last',lastCluster)] = 1

    return dict(features)




def general_inquirer_features(phrase):

    features = {}

    #Add General Inquirer Features
    lastTags = None
    tagDict = defaultdict(lambda:0)
    for word in phrase:
        #print word
        negated = ('_neg' in word)
        if negated: word = word[:-4]

        weight = 1 if not negated else 0

        wordTags = lexInq.getTags(word)
        #print 'wordTags: ', wordTags
        if wordTags != None:
            for tag in wordTags:
                #print '\t', tag
                tagDict[tag] += weight
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
        uni_scores = []
        for word in phrase:
            score = context_lookup( lambda w: lex.lookupUnigram(w).score, word)
            uni_scores.append(score)

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

    # Not including will boost results
    #features.update(     brown_cluster_features(phrase)                  )

    # Apply all general-purpose lexicons
    features.update( subjectivity_lexicon_features(phrase)                  )

    features.update(        affin_lexicon_features(phrase)                  )



    features.update(   emotion_lexicon_features(phrase)                  )
    features.update(     general_inquirer_features(phrase)                  )

    #if features:
    #    print phrase
    #    print features
    #    print '\n\n'

    return { k:v for k,v in features.items() if v }

