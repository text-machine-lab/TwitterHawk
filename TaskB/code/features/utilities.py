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
import nltk

from BeautifulSoup import BeautifulSoup
from HTMLParser    import HTMLParser

from read_config import enabled_modules


# Add lexicon code to path
if enabled_modules['lexicons']:
    sys.path.append( os.path.join(enabled_modules['lexicons'] ,'code') )
else:
    sys.path.append( os.path.join(os.getenv('BISCUIT_DIR') ,'lexicons/code') )
import emoticons


if enabled_modules['twitter_nlp']:
    from nlp import nlp



def tokenize(text, nlp=None):

    # Use twitter_nlp tokenzier, if available
    if nlp:
        return nlp.tokens(text)
    else:
        return text.split()



def normalize_phrase(phrase, stem=False):

    """
    normalize()

    Purpose: Normalize tweet phrases (ex. make user mentions & URLs generic)

    @param phrase.  A list of words from a tweet (ex. [     '@foo', 'does', 'not', 'like'    ] )
    @return         A normalized list of words   (ex. ['@someuser', 'does', 'not', 'like_neg'] )
    """

    retVal = []


    # Stem words
    st = nltk.stem.PorterStemmer()

    negated = False
    end_negated = False
    for word in phrase:

        # Empty word
        if not word:
            negated = False

        # Emoticon
        elif emoticons.emoticon_type(word):
            if negated: word += '_neg'
            retVal.append(word)

        # Punctuation
        elif all( [ (c in string.punctuation) for c in word ] ):
            negated = False
            # Emoticon

        # User mention
        elif word[0] == '@':
            negated = False
            retVal.append('@someuser')

        # Hashtag
        elif word[0] == '#':
            negated = False
            retVal.append(word.lower())

        # URL
        elif is_url(word):
            negated = False
            retVal.append('http://someurl')

        # Negation
        elif is_negation(word):
            negated = True
            retVal.append(word)

        # Simple word
        else:
            if stem:
                word = word.lower()
                #word = word.strip(string.punctuation)
                word = st.stem(word)
            if negated: word = word + '_neg'
            retVal.append(word)

    return retVal



def is_url(word):

    """
    isUrl()

    Purpose: Determine if a word is a URL

    @param word.   Any word from a tweet
    @return        A boolean indicating True is 'word' is a URL, false otherwise
    """

    if re.search('http://',word): return True
    if re.search(  'www\.',word): return True
    if re.search(  '\.com',word): return True
    if re.search(  '\.net',word): return True
    if re.search(  '\.org',word): return True

    return False



def is_negation(word):

    """
    isNegation()

    Purpose: Determine if a word is negative

    @param word.   Any word from a tweet
    @return        A boolean indicating True is 'word' is negative, false otherwise
    """

    word = word.lower()

    if word == 'no'     : return True
    if word == 'not'    : return True
    if word == 'none'   : return True
    if word == 'nobody' : return True
    if word == 'nothing': return True
    if word == 'nowhere': return True
    if word == 'never'  : return True
    if word == 'neither': return True

    if re.search(".*n't", word): return True

    return False



def StopWords():

    """
    StopWords()

    Purpose: Get a list of stop words for English

    Source: http://alvinalexander.com/java/jwarehouse/lucene/src/java/org/apache/lucene/analysis/StopAnalyzer.java.shtml

    @return  A set of stopwords
    """

    sw = frozenset( ["a"   , "an"   , "and"  , "are" , "as"  , "at"   ,
                     "be"  , "but"  , "by"   , "for" , "if"  , "in"   ,
                     "into", "is"   , "it"   , "no"  , "not" , "of"   ,
                     "on"  , "or"   , "such" , "that", "the" , "their",
                     "then", "there", "these", "they", "this", "to"   ,
                     "was" , "will" , "with"                          ] )

    return sw



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

