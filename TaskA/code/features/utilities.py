#-------------------------------------------------------------------------------
# Name:        utilities.py
#
# Purpose:     Miscellaneous tools (ex. normalizing tweets)
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import sys
import os
import re
import string
import nltk


# Add lexicon code to path
sys.path.append( os.path.join(os.getenv('BISCUIT_DIR'),'lexicons/code') )
from emoticons import emoticon_type




def split_hashtag(word):

    """
    split_hashtag()

    Purpose: Try to build list of words in hashtag concatentation
             ( ex. "#CurrentEvents"  ->  ["Current", "Events"] )

    @param  word.   A string beginning with a "#"
    @return         A list of words of the tokenized hashtag word
    """

    retVal = []

    #print '\t\tHT: ', word

    # Assume CamelCase
    toks = re.findall('([a-z]+|[A-Z][a-z]+|[0-9]+)', word)
    if toks:
        retVal = toks
        #for o in toks:
        #    print '\t\t\t', o

    else:
        retVal = [word]

    return retVal



def normalize_phrase(phrase):

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
    for word in phrase:

        # Empty word
        if not word:
            retVal.append('')

        # User mention
        elif word[0] == '@':
            retVal.append('@someuser')

        # Hashtag
        elif word[0] == '#':
            # Split hashtag word
            toks = split_hashtag(word)
            HT_negated = False
            for w in toks:
                #w = st.stem(w.lower())
                w = w.lower()

                if isNegation(w):
                    HT_negated = not HT_negated
                else:
                    if HT_negated: w = w + '_neg'

                retVal.append(w)

        # URL
        elif isUrl(word):
            retVal.append('http://someurl')

        # Negation
        elif isNegation(word):
            negated = not negated
            retVal.append(word)

        # Emoticon
        elif emoticon_type(word):
            if negated: word = word + '_neg'
            retVal.append(word)

        # Simple word
        else:
            if word in StopWords(): continue

            word = word.lower()
            word = word.strip(string.punctuation)  # (major improvements in F1)
            word = st.stem(word)

            if negated: word = word + '_neg'
            retVal.append(word)


    return set(retVal)



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
