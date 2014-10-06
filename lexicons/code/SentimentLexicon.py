#-------------------------------------------------------------------------------
# Name:        SentimentLexicon.py
#
# Purpose:     Interface for HashtagSentiment  and  Sentiment140  data
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


from collections import defaultdict
import sys
import os




BASE_DIR = os.path.join(os.getenv('BISCUIT_DIR'),'lexicons')


# Organize Data
class SentimentTriple:
    def __init__(self, s, p, n):
        self.score       = s
        self.numPositive = p
        self.numNegative = n

    def __str__(self):
        return str(self.score) + '  ' + str(self.numPositive) + '  ' + str(self.numNegative)




class SentimentLexicon:

    def __init__(self, lex_name):

        #Store data
        self._unigrams = defaultdict(lambda:SentimentTriple(0,0,0))
        self._bigrams  = defaultdict(lambda:SentimentTriple(0,0,0))


        # Files containing data
        lexicon_dir = os.path.join(os.path.join(BASE_DIR,'lexicons'), lex_name)
        unigrams_f = os.path.join(lexicon_dir, 'unigrams-pmilexicon.txt')
        bigrams_f  = os.path.join(lexicon_dir,  'bigrams-pmilexicon.txt')


        # Populate table with unigrams
        if os.path.exists(unigrams_f):
            with open(unigrams_f, 'r') as f:
                for line in f.readlines():
                    data = line.split()
                    self._unigrams[data[0]] = SentimentTriple( float(data[1]) ,
                                                                 int(data[2]) ,
                                                                 int(data[3]) )
        else:
            print >>sys.stderr, 'ERROR: Unable to read unigrams from lexicon: ', lex_name


        # Populate table with bigrams
        if os.path.exists(bigrams_f):
            with open(bigrams_f, 'r') as f:
                for line in f.readlines():
                    data = line.split()
                    key = data[0], data[1]
                    self._bigrams[key] = SentimentTriple( float(data[2]) ,
                                                            int(data[3]) ,
                                                            int(data[4]) )
        else:
            print >>sys.stderr, 'ERROR: Unable to read bigrams lexicon: ', lex_name


    def lookupUnigram(self, unigram):
        return self._unigrams[unigram]

    def lookupBigram(self, bigram):
        return self._bigrams[bigram]

