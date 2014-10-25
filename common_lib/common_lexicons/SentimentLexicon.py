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


# Add common-lib code to system path
sources = os.getenv('BISCUIT_DIR')
if sources not in sys.path: sys.path.append(sources)

from common_lib.read_config import enabled_modules




# Organize Data
class SentimentTriple:
    def __init__(self, s, p, n):
        self.score       = s
        self.numPositive = p
        self.numNegative = n

    def __str__(self):
        return '(' + str(self.score) + '  ' + str(self.numPositive) + '  ' + str(self.numNegative) + ')'




class SentimentLexicon:

    def __init__(self, lex_name):

        #Store data
        self._unigrams = defaultdict(lambda:SentimentTriple(0,0,0))
        self._bigrams  = defaultdict(lambda:SentimentTriple(0,0,0))
        self._pairs    = defaultdict(lambda:SentimentTriple(0,0,0))


        # Files containing data
        base_dir = enabled_modules['lexicons']
        lexicon_dir = os.path.join(base_dir, lex_name)
        unigrams_f = os.path.join(lexicon_dir, 'unigrams-pmilexicon.txt')
        bigrams_f  = os.path.join(lexicon_dir,  'bigrams-pmilexicon.txt')
        pairs_f    = os.path.join(lexicon_dir,    'pairs-pmilexicon.txt')


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

        # Populate table with pairs 
        if os.path.exists(pairs_f):
            with open(pairs_f, 'r') as f:
                for line in f.readlines():
                    data = line.split('\t')
                    toks = data[0].split('---')

                    # If ensure all bi-uni are stored as uni-bi
                    if len(toks[0].split()) == 2 and len(toks[1].split()) == 1:
                        toks = [ toks[0], toks[1] ]

                    toks = tuple(toks)
                    self._pairs[toks] = SentimentTriple( float(data[1]) ,
                                                           int(data[2]) ,
                                                           int(data[3]) )
        else:
            print >>sys.stderr, 'ERROR: Unable to read pairs from lexicon: ', lex_name



    def lookupUnigram(self, unigram):
        return self._unigrams[unigram]

    def lookupBigram(self, bigram):
        return self._bigrams[bigram]

    def lookupPair(self, pair):
        return self._pairs[pair]
