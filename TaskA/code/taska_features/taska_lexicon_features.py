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




def lexicon_normalize(phrase):
    punc = string.punctuation.replace('#','')
    return [  word.lower().strip(punc)  for  word  in  phrase  ]



def max0(lst):
    """ Calls max but gives default of 0 is list is empty """
    if not lst: return 0
    return max(lst)



def lexicon_features(phrase):

    """
    features_for_word()

    @param word. A word from a tweet
    @return      A feature dictionary
    """

    features = {}

    # Slight normalization
    phrase = [  w.lower()  for  w  in  phrase  ]
    phrase = lexicon_normalize(phrase)

    # Features: Opinion & Subjectivity Classifications
    for word in phrase:
        lexOpi_label = lexOpi.lookup(word)
        features[ ('lexOpi_unigram',lexOpi_label) ] = 1

        lexSubj_label = lexSubj.lookup(word).prior
        features[ ('lexSubj_unigram',lexSubj_label) ] = 1


    # Features: Sentiment Scores
    lexHTS_uni_scores  = []
    lexS140_uni_scores = []
    for word in phrase:
        lexHTS_uni_scores.append(   lexHTS.lookupUnigram(word).score )
        lexS140_uni_scores.append( lexS140.lookupUnigram(word).score )


    '''
    print '\tphrase: ', phrase
    print '\tHTS :   ', lexHTS_uni_scores
    print '\tS140:   ', lexS140_uni_scores
    print
    '''


    polarities = polarity_count('HTS', lexHTS_uni_scores)


    '''
    print polarities
    print

    return features
    '''


    # Three most influential sentiments
    inf_uni_HTS = sorted(lexHTS_uni_scores,key=abs,reverse=True)
    for i,score in enumerate(inf_uni_HTS[:3]):
        featname = ('lexHTS_unigram-influential-%d' % i, None)
        features[featname] = score

    inf_uni_S140 = sorted(lexS140_uni_scores,key=abs,reverse=True)
    for i,score in enumerate(inf_uni_S140[:3]):
        featname = ('lexS140_unigram-influential-%d' % i, None)
        features[featname] = score


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


    # Average scores
    features[('avg_HTS' ,None)] = max0(inf_uni_HTS ) / (sum(inf_uni_HTS ) + 1e-5)
    features[('avg_S140',None)] = max0(inf_uni_S140) / (sum(inf_uni_S140) + 1e-5)


    emo_scores = defaultdict(lambda:[])
    for e,score in reversed(inf_uni_Emo):
        emo_scores[e].append(score)
    for e,scores in emo_scores.items():
        featname = ('avg_Emo-' + e, None)
        features[featname] = max0(scores ) / (sum(scores ) + 1e-5)




    # Features; Bigram Senitment Scores
    lexHTS_bi_scores  = []
    lexS140_bi_scores = []
    for i in range(len(phrase) - 1):
        bigram = phrase[i], phrase[i+1]
        lexHTS_bi_scores.append(   lexHTS.lookupUnigram(bigram).score )
        lexS140_bi_scores.append( lexS140.lookupUnigram(bigram).score )

    inf_bi_HTS = sorted(lexHTS_bi_scores,key=abs,reverse=True)
    for i,score in enumerate(inf_bi_HTS):
        featname = ('lexHTS_bigram-influential-%d' % i, None)
        features[featname] = score

    inf_bi_S140 = sorted(lexS140_bi_scores,key=abs,reverse=True)
    for i,score in enumerate(inf_bi_S140):
        featname = ('lexS140_bigram-influential-%d' % i, None)
        features[featname] = score


    '''
    # Average scores
    #print inf_HTS
    features['avg_bigram_HTS' ] = max0(inf_bi_HTS ) / (sum(inf_bi_HTS ) + 1e-5)
    features['avg_bigram_S140'] = max0(inf_bi_S140) / (sum(inf_bi_S140) + 1e-5)
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

