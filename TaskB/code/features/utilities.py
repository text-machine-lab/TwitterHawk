#-------------------------------------------------------------------------------
# Name:        utilities.py
#
# Purpose:     Miscellaneous tools (ex. normalizing tweets)
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import re
import string
import nltk



def normalize_phrase(phrase):

    """
    normalize()

    Purpose: Normalize tweet phrases (ex. make user mentions & URLs generic)

    @param phrase.  A list of words from a tweet (ex. [     '@foo', 'does', 'not', 'like'    ] )
    @return         A normalized list of words   (ex. ['@someuser', 'does', 'not', 'like_neg'] )
    """

    retVal = []

    negated = False
    for word in phrase:

        # User mention
        if word[0] == '@':
            retVal.append('@someuser')

        # URL
        elif isUrl(word):
            retVal.append('http://someurl')

        # Negation
        elif isNegation(word):
            negated = not negated
            retVal.append(word)

        # Simple word
        else:
            if word in StopWords(): continue

            st = nltk.stem.PorterStemmer()
            word = st.stem(word)

            if negated: word = word + '_neg'
            retVal.append(word)

    return retVal



def isUrl(word):

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



def isNegation(word):

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



def isElongatedWord(word):

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



def isElongatedPunctuation(word):

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



def stripPunctuation(phrase):

    """
    stripPunctuation()

    Purpose: NOT SURE

    @param phrase.  A list of words from a tweet
    @return         A list of words from a tweet without punctuation
    """

    punc = string.punctuation.replace('#','')

    return [  word.strip(punc)  for  word  in  phrase  ]