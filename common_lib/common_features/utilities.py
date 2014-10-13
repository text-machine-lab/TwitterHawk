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

from BeautifulSoup import BeautifulSoup
from HTMLParser    import HTMLParser


# Add common-lib code to system path
sources = os.getenv('BISCUIT_DIR')
if sources not in sys.path: sys.path.append(sources)
from read_config import enabled_modules

from common_lib.common_lexicons import emoticons



# Negative words
neg_words  = frozenset(['no', 'not', 'none', 'nobody', 'nothing', 
                        'nowhere', 'never', 'neither'])

# Stop words
stop_words = frozenset( ["a"   , "an"   , "and"  , "are"  , "as"  , "at"   ,
                         "be"  , "but"  , "by"   , "for"  , "if"  , "in"   ,
                         "into", "is"   , "it"   , "no"   , "not" , "of"   ,
                         "on"  , "or"   , "such" , "that" , "the" , "their",
                         "then", "there", "these", "they" , "this", "to"   ,
                         "was" , "will" , "with" ,                        ] )


# Stemmer for words
st = nltk.stem.SnowballStemmer('english')



def tokenize(text, nlp=None):

    # Use twitter_nlp tokenzier, if available
    if nlp:
        return nlp.tokens(text)
    else:
        return text.split()



# Slightly different for TaskA vs. TaskB
def normalize_phrase_TaskA(phrase, stem=False):
    return normalize_phrase(phrase, stem)


def normalize_phrase_TaskB(phrase, stem=False):
    return [   w   for tok in normalize_phrase(phrase,stem)   for w in tok   ]



def normalize_phrase(phrase, stem=False):

    """
    normalize()

    Purpose: Normalize tweet phrases (ex. make user mentions & URLs generic)

    @param phrase.  A list of words from a tweet 
    @return         A normalized list of list of tokens.

    NOTE: Must be list of list because TaskA's token indices must not change.

    example:
         phrase ->    (ex. [     '@foo'  ,  'hates' , '#Dumb#Guys']       )
         return ->    (ex. [['@someuser'], ['hates'], ['#Dumb', '#Guys']] )
    """

    retVal = []


    negated = False
    end_negated = False
    for w in phrase:

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
            #tok = [word]
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

        # Un-cleaned HTML stopword
        elif word == '&amp;':
            tok = []

        # Simple word
        else:
            done_neg = (word[-1] in string.punctuation)

            word = word.strip(string.punctuation)
            if word in stop_words:
                tok = []
            else:
                if stem:
                    word = st.stem(word)
                if negated: word = word + '_neg'
                tok = [word]

            if done_neg: negated = False


        # Append list of tokens (and retain original indices)
        retVal.append(tok)

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

