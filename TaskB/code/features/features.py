#-------------------------------------------------------------------------------
# Name:        features.py
#
# Purpose:     Extract features
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import emoticons
import utilities
from lexicons.lexicons import lexHTS, lexS140, lexOpi, lexSubj, lexEmo




def features_for_tweet(tweet):

    """
    Model::features_for_tweet()

    Purpose: Generate features for a single tweet

    @param tweet. A string (the text of a tweet)
    @return       A hash table of features
    """

    # Tweet representation
    phrase = tweet.split()


    # Normalize tweet
    #normalized = utilities.normalize_phrase(phrase)
    normalized = phrase


    # Feature: Dummy ( always have >0 dimensions )
    #features = { ('dummy','dummy') : 1}
    features = {}


    # Term unigrams
    for word in normalized:
        features[('term_unigram', word)] = 1


    # These don't do much
    features['first_unigram'] = phrase[ 0]
    features[ 'last_unigram'] = phrase[-1]


    return features


    features['phrase_length'] = len(phrase) / 15


    # Feature: Prefixes and Suffixes
    n = [2,3]
    for i,word in enumerate(normalized):
        for j in n:
            if word[-4:] == '_neg': word = word[:-3]

            prefix = word[:j]
            suffix = word[-1-j+1:]

            features[ ('prefix',prefix) ] = 1
            features[ ('suffix',suffix) ] = 1




    '''
    # Feature: Bigrams
    for i in range(len(phrase) - 1):
        ngram = ' '.join(normalized[i:i+2])
        features[ ('bigram',ngram) ] = 1
    '''


    '''
    # Rating: Not great
    # Feature: All Caps? (boolean)
    is_all_caps = True
    for word in phrase:
        if word != word.upper():
            is_all_caps = False
            break
    features[ ('all_caps',is_all_caps) ] = 1
    '''

    '''
    # Rating: Hardly useful
    # Feature: All Stopwords? (boolean)
    sw = utilities.StopWords()
    is_all_stopwords = True
    for word in phrase:
        if not word in sw:
            is_all_stopwords = False
            break
    features[ ('is_all_stopwords',is_all_stopwords) ] = 1
    '''


    '''
    # Rating: Might be good (unsure) bad
    # Feature: Contains elongated long word? (boolean)
    contains_elongated_word = False
    for word in phrase:
        if utilities.isElongatedWord(word):
            contains_elongated_word = True
            break
    features[ ('contains_elongated_word',contains_elongated_word) ] = 1
    '''


    '''
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
        print featname, ' - ', v
    print ''
    '''


    '''
    # Not useful
    # Feature: All Capitalization? (boolean)
    is_all_capitalization = True
    for word in phrase:
        if word[0].islower():
            is_all_capitalization = False
            break
    features[ ('all_capitalization',is_all_capitalization) ] = 1
    '''


    '''
    # Rating: Bad :(
    # Feature: Punctuation counts
    punct = {'!':0, '?':0}
    for c in ''.join(phrase):
        if c in punct: punct[c] += 1
    for k,v in punct.items():
        featname = k + '-count'
        features[featname]= v
    '''

    return features


    # Feature: Lexicon Features
    feats = lexicon_features(phrase)
    features.update(feats)

    return features



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


    # Features: Opinion & Subjectivity Classifications
    features = {}
    for word in phrase:
        lexOpi_label = lexOpi.lookup(word)
        features[ ('lexOpi_unigram',lexOpi_label) ] = 1

        lexSubj_label = lexSubj.lookup(word).prior
        features[ ('lexSubj_unigram',lexSubj_label) ] = 1


    # Features: Sentiment Scores
    lexHTS_scores  = []
    lexS140_scores = []
    for word in phrase:
        lexHTS_scores.append(   lexHTS.lookupUnigram(word).score )
        lexS140_scores.append( lexS140.lookupUnigram(word).score )

    # Three most influential sentiments
    inf_HTS = sorted(lexHTS_scores,key=abs,reverse=True)
    for i,score in enumerate(inf_HTS[:3]):
        featname = 'lexHTS_unigram-influential-%d' % i
        features[featname] = score

    inf_S140 = sorted(lexS140_scores,key=abs,reverse=True)
    for i,score in enumerate(inf_S140[:3]):
        featname = 'lexS140_unigram-influential-%d' % i
        features[featname] = score


    # Features: Emotion Scores
    lexEmo_scores = []
    for word in phrase:
        lexEmo_scores.append(lexEmo.lookup(word))

    # Three most influential emotions
    inf_Emo = sorted(lexEmo_scores,key=lambda t:t[1])
    for i,tup in enumerate(inf_Emo[-3:]):
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
    lexHTS_scores  = []
    lexS140_scores = []
    for i in range(len(phrase) - 1):
        bigram = phrase[i], phrase[i+1]
        lexHTS_scores.append(   lexHTS.lookupUnigram(bigram).score )
        lexS140_scores.append( lexS140.lookupUnigram(bigram).score )

    inf_HTS = sorted(lexHTS_scores,key=abs,reverse=True)
    for i,score in enumerate(inf_HTS):
        featname = 'lexHTS_bigram-influential-%d' % i
        features[featname] = score

    inf_S140 = sorted(lexS140_scores,key=abs,reverse=True)
    for i,score in enumerate(inf_S140):
        featname = 'lexS140_bigram-influential-%d' % i
        features[featname] = score


    '''
    # Average scores
    #print inf_HTS
    features['avg_bigram_HTS' ] = max(inf_HTS ) / (sum(inf_HTS ) + 1e-5)
    features['avg_bigram_S140'] = max(inf_S140) / (sum(inf_S140) + 1e-5)
    '''


    return features


