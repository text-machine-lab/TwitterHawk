#-------------------------------------------------------------------------------
# Name:        lexicon.py
#
# Purpose:     Lexicon features
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import os,sys
import string
from collections import defaultdict

from read_config import enabled_modules

if not enabled_modules['lexicons']:
    print >>sys.stderr, 'cannot find lexicons'
    exit()

sys.path.append( os.path.join(enabled_modules['lexicons'],'code') )
from lexicons import lexHTS, lexS140, lexOpi, lexSubj, lexEmo



def normalize(phrase):
    punc = string.punctuation.replace('#','')
    return [  word.lower().strip(punc)  for  word  in  phrase  ]



def lexicon_features(phrase):

    """
    lexicon_features()

    @param word. A split list of words from a tweet.
    @return      A feature dictionary.
    """

    # Slight normalization
    phrase = normalize(phrase)


    features = {}


    # Features: Opinion Classification
    Opi_sentiments = defaultdict(lambda:0)
    for word in phrase:
        label = lexOpi.lookup(word)
        Opi_sentiments[label] += 1
    for sentiment,count in Opi_sentiments.items():
        if sentiment ==        '': continue
        if sentiment == 'neutral': continue
        features[ 'Opi-%s_count' % sentiment ] = count * 2



    # Feature Subjectivity Classification
    Subj_sentiments = defaultdict(lambda:0)
    for word in phrase:
        label = lexSubj.lookup(word).prior
        Subj_sentiments[label] += 1
    for sentiment,count in Subj_sentiments.items():
        if sentiment ==        '': continue
        if sentiment == 'neutral': continue
        features[ 'Subj-%s_count' % sentiment ] = count * 2



    # Sentiment Scores
    lexHTS_uni_scores  = [   lexHTS.lookupUnigram(w).score  for  w  in  phrase  ]
    lexS140_uni_scores = [  lexS140.lookupUnigram(w).score  for  w  in  phrase  ]

    '''
    for w,s in zip(phrase,lexHTS_uni_scores):
        print s, w
    exit()
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

    features['avg_HTS' ] = sum(inf_uni_HTS ) / (len(inf_uni_HTS ) + 1e-5)
    features['avg_S140'] = sum(inf_uni_S140) / (len(inf_uni_S140) + 1e-5)



    pos_uni_HTS_scores  = [  s  for  s  in   lexHTS_uni_scores  if  s > 0  ]
    pos_uni_S140_scores = [  s  for  s  in  lexS140_uni_scores  if  s > 0  ]

    # Features: Hashtag Sentiment features
    features['HTS-uni-sum'           ]  = sum(lexHTS_uni_scores)
    features['HTS-uni-positive_count']  = len(pos_uni_HTS_scores)
    if len(pos_uni_HTS_scores):
        features['HTS-uni-max'      ]  = max(pos_uni_HTS_scores)
        features['HTS-uni-last_pos'] = pos_uni_HTS_scores[-1]

    # Features: Sentiment 140 features
    features['S140-uni-sum'           ] = sum(lexS140_uni_scores)
    features['S140-uni-positive_count'] = len(pos_uni_S140_scores)
    if len(pos_uni_S140_scores):
        features['S140-uni-max'      ] = max(pos_uni_S140_scores)
        features['S140-uni-last_pos'] = pos_uni_S140_scores[-1]



    # Emotion Scores
    lexEmo_uni_scores = defaultdict(lambda:[])
    for w in phrase:
        senti = lexEmo.lookup(w)
        lexEmo_uni_scores[senti[0]].append( senti[1] )

    # Features: Sentiment 140 features
    for e,scores in lexEmo_uni_scores.items():
        pos  = [  s  for  s  in  scores  if  s > 0  ]
        features[ 'Emo-uni-%s-sum'            % e ] = sum(scores)
        features[ 'Emo-uni-%s-positive_count' % e ] = len(pos)
        if len(pos):
            features[ 'Emo-uni-%s-max'       % e ] = max(pos)
            features[ 'Emo-uni-%s-last_pos' % e ] = pos[-1]

    # Three most influential emotions
    for e,scores in lexEmo_uni_scores.items():
        inf_Emo = sorted(scores, reverse=True)
        for i,score in enumerate(inf_Emo[:3]):
            featname = ('Emo-unigram-influential-%d'%i, e)
            features[featname] = score
        features[('Emo-count',e)] = len(scores)




    # Result: Good
    # Features: Bigram Senitment Scores
    lexHTS_bi_scores  = []
    lexS140_bi_scores = []
    for i in range(len(phrase) - 1):
        bigram = phrase[i], phrase[i+1]
        lexHTS_bi_scores.append(   lexHTS.lookupBigram(bigram).score )
        lexS140_bi_scores.append( lexS140.lookupBigram(bigram).score )

    inf_bi_HTS = sorted(lexHTS_bi_scores,key=abs,reverse=True)
    for i,score in enumerate(inf_bi_HTS[:3]):
        featname = 'lexHTS_bigram-influential-%d' % i
        features[featname] = score

    inf_bi_S140 = sorted(lexS140_bi_scores,key=abs,reverse=True)
    for i,score in enumerate(inf_bi_S140[:3]):
        featname = 'lexS140_bigram-influential-%d' % i
        features[featname] = score


    '''
    # Result: Not helpful
    # Average scores
    features['avg_bigram_HTS' ] = sum(inf_bi_HTS ) / (len(inf_bi_HTS ) + 1e-5)
    features['avg_bigram_S140'] = sum(inf_bi_S140) / (len(inf_bi_S140) + 1e-5)
    '''


    # Result: Good (doesn't mix well with other bigram features)
    pos_bi_HTS_scores  = [  s  for  s  in   lexHTS_bi_scores  if  s > 0  ]
    pos_bi_S140_scores = [  s  for  s  in  lexS140_bi_scores  if  s > 0  ]

    features['HTS-bi-sum'           ]  = sum(lexHTS_bi_scores)
    features['HTS-bi-positive_count']  = len(pos_bi_HTS_scores)
    if len(pos_bi_HTS_scores):
        features['HTS-bi-max'      ]  = max(pos_bi_HTS_scores)
        features['HTS-bi-last_pos'] = pos_bi_HTS_scores[-1]

    features['S140-bi-sum'           ]  = sum(lexS140_bi_scores)
    features['S140-bi-positive_count']  = len(pos_bi_S140_scores)
    if len(pos_bi_S140_scores):
        features['S140-bi-max'      ]  = max(pos_bi_S140_scores)
        features['S140-bi-last_pos'] = pos_bi_S140_scores[-1]


    #print features
    #print 

    return features

