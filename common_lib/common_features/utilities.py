#-------------------------------------------------------------------------------
# Name:        utilities.py
#
# Purpose:     Miscellaneous tools (ex. normalizing tweets)
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import sys, os
import re
import string
import nltk.stem
import numpy as np
from HTMLParser import HTMLParser


# Add common-lib code to system path
sources = os.getenv('BISCUIT_DIR')
if sources not in sys.path: sys.path.append(sources)
from common_lib.read_config import enabled_modules

from common_lib.common_lexicons import emoticons


# Negative words
neg_words  = frozenset(['no', 'not', 'none', 'nobody', 'nothing', 
                        'nowhere', 'never', 'neither'])

# Stop words
stop_words = frozenset( ["a"   , "an"   , "and"  , "are"  , "as"  , "at"   ,
                         "be"  , "but"  , "by"   , "for"  , "if"  , "in"   ,
                         "into", "is"   , "it"   ,                  "of"   ,
                         "on"  , "or"   , "such" , "that" , "the" , "their",
                         "then", "there", "these", "they" , "this", "to"   ,
                         "was" , "will" , "with"                           ] )


# Stemmer for words
st = nltk.stem.SnowballStemmer('english')


# Cleaning up text if ark_tweet not available
h = HTMLParser()


# Memo-ize tokenization of TaskA sentences (because multiple phrase instances per sentence)
taska_tokenizations = []


def tokenize(text, ark_tweet=None):

    # Use twitter_nlp tokenzier, if available
    if ark_tweet:
        return ark_tweet.tokens(text)
    else:
        return text.split()



# Slightly different for TaskA vs. TaskB
def normalize_phrase_TaskA(sentence, ark_tweet=None, stem=False):

    # Form full string of text
    if ark_tweet:
        text = ark_tweet.normalizeKey( ' '.join(sentence) )
    else:
        clean = lambda txt: h.unescape(txt).strip()
        text = clean(clean(' '.join(sentence)))


    # Save character index that each token ends at
    text = text.replace('\n', ' ').replace('\t', ' ')
    curr = len(text.split(' ')[0])
    indices = [curr]
    for w in text.split(' ')[1:]:
        curr += len(w) + 1
        indices.append(curr)


    '''
    # Test that indices are correct: recover original tokens from text
    start = 0
    reconstructed = []
    for ind in indices[1:]:
        print 'start/end: ', start, ind
        print '\t~~~' + text[start:ind-1] + '~~~'
        reconstructed.append(text[start:ind-1])
        start = ind
    reconstructed.append(text[start:])
    '''

    # Tokenize
    toks = tokenize(text, ark_tweet)


    #print 'sent: ', sentence
    #print
    #print 'text: ', text
    #print
    #print 'indices: ', indices
    #print
    #print 'toks: ', toks
    #print


    detoks = []
    aggregate = []
    ind = 0
    curr = 0
    for tok in toks:

        #print '\t', tok
        #print curr
        #print indices[ind]


        # empty token
        while curr == indices[ind]:
            #print '$$   ', indices[ind]
            detoks.append([''])
            ind += 1
            curr += 1
            

        curr += len(tok)

        aggregate.append(tok)

        if curr == indices[ind]:
            #print '---'
            detoks.append(aggregate)
            aggregate = []
            ind += 1
            curr += 1

    #print 'detoks: ', detoks
    #print
    #print 'reconstructed: ', reconstructed
    #print '\n\n'

    return normalize_phrase(detoks, stem)


def normalize_phrase_TaskB(sentence, stem=False):
    # Unflatten list of list of tokens
    return [  w   for tok in normalize_phrase([sentence],stem)   for w in tok  ]



def normalize_phrase(phrase, stem=False):

    """
    normalize()

    Purpose: Normalize tweet phrases (ex. make user mentions & URLs generic)

    @param phrase.  A list of list of tokens from a tweet 
    @return         A normalized list of list of tokens.

    NOTE: Must be list of list because TaskA's token indices must not change.

    example:
         phrase ->    (ex. [     ['@foo']  ,  ['hates'] , ['#Dumb#Guys'    ]] )
         return ->    (ex. [['@someuser']  , ['hates']  , ['#Dumb', '#Guys']] )
    """

    retVal = []

    #print '\n\n\n'
    #print 'phrase: ', phrase

    negated = False
    for words in phrase:

        toks = []

        for w in words:

            word = w.lower()

            # Empty word
            if not word:
                negated = False
                tok = []

            # Number
            elif is_number(word):
                tok =['<generic#>']

            # Negation
            elif is_negation(word):
                negated = True
                tok = [word]

            # Emoticon
            elif emoticons.emoticon_type(w):
                if negated: word += '_neg'
                tok = [w]

            # Punctuation
            elif all( [ (c in string.punctuation) for c in word ] ):
                negated = False
                # All exlamation marks?
                if   re.search('!+',word):
                    tok = ['!']
                elif re.search('\\?+',word):
                    tok = ['?']
                else:
                    tok = []

            # User mention
            elif word[0] == '@':
                negated = False
                tok = ['@someuser']

            # Hashtag
            elif '#' in word:
                negated = False
                matches = w.split('#')
                tok = []
                if matches[0]: tok.append(matches[0])
                for ht in matches[1:]:
                    if ht: tok.append('#'+ht)

            # URL
            elif is_url(word):
                negated = False
                tok = ['http://someurl']

            # Simple word
            else:
                word = word.strip(string.punctuation)
                if word in stop_words:
                    tok = []
                else:
                    if stem:
                        word = word.decode('ascii','ignore')
                        word = st.stem(word)
                    if negated: word = word + '_neg'
                    tok = [word]

            toks += tok

        # Append list of tokens (and retain original indices)
        retVal.append(toks)

    #print
    #print retVal

    return retVal




def is_number(n):
    if n.isalpha(): return False
    try:
        float(n)
        return True
    except ValueError:
        return False



def is_url(word):

    """
    isUrl()

    Purpose: Determine if a word is a URL

    @param word.   Any word from a tweet
    @return        A boolean indicating True is 'word' is a URL, false otherwise
    """

    if word[:7]  == 'http://': return True
    if word[:4]  == 'www.'   : return True
    if word[-4:] ==    '.com': return True
    if word[-4:] ==    '.net': return True
    if word[-4:] ==    '.org': return True

    return False



def is_negation(word):

    """
    isNegation()

    Purpose: Determine if a word is negative

    @param word.   Any word from a tweet
    @return        A boolean indicating True is 'word' is negative, false otherwise
    """

    #word = word.lower()

    if word in neg_words:  return True

    if word[-3:] == "n't": return True

    return False



def is_elongated_word(word):

    """
    isElongatedWord()

    Purpose: Determine if a word is elongated (ex. "heyyy")

    @param word.   A word from a tweet
    @return        A boolean indicating True for elongated word, False otherwise
    """

    # Normalize
    word = word.lower()

    # If same letter repeated three times
    for i in range(len(word)-2):
        if not word[i].isalpha(): continue
        # This syntax for triple equality is allowed in Python
        if word[i] == word[i+1] == word[i+2]:
            return True

    # No matches
    return False



def is_elongated_punctuation(word):

    """
    isElongatedPunctuation()

    Purpose: Determine if a word is elongated (ex. "well...")

    @param word.   A word from a tweet
    @return        A boolean indicating True for elongated punctuation, False otherwise
    """

    # Normalize
    word = word.lower()

    # If same letter repeated three times
    for i in range(len(word)-2):
        if word[i].isalpha(): continue
        # This syntax for triple equality is allowed in Python
        if word[i] == word[i+1] == word[i+2]:
            return True

    # No matches
    return False


def normalize_data_matrix(X):
    print X
    meanVector = np.mean(X, axis=0)
    stdVector = np.std(X, axis=0)
    for i,comp in enumerate(stdVector):
        if comp == 0:
            stdVector[i] = 1.
    meanMatrix = np.kron(np.ones((X.shape[0], 1)), meanVector)
    stdMatrix = np.kron(np.ones((X.shape[0], 1)), stdVector)
    return (X-meanMatrix)/stdMatrix
