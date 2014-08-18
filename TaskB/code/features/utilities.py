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

from BeautifulSoup import BeautifulSoup
from HTMLParser    import HTMLParser

from UrlWrapper import urlopen
from emoticons import emoticon_type



def normalize_url(url):

    """
    normalize_url()

    Purpose: Resolve URL to gain additional insight into url (domain name, subject title, etc)

    @param url.  A tiny url from a tweet.
    @return      A list of unigrams from the subject title
    """

    return ['http//someurl']

    print '\t', url

    # Return a set of unigrams
    retVal = []


    # Follow url
    try:
        uf  = urlopen(url)
        content = uf.read()
        link = uf.geturl()
        soup = BeautifulSoup(content)

    except Exception,e:
        print 'Read Error -- ', e, ': ', url
        print
        return []


    # Get title
    if soup.title:
        st = nltk.stem.PorterStemmer()
        h = HTMLParser()

        negated = False
        title = h.unescape( soup.title.getText(' ') )
        for w in title.split():

            if not w: continue

            if isNegation(w):
                negated = True
                retVal.append(w)
                continue

            w = w.lower()
            w = w.strip(string.punctuation)

            if negated:
                retVal += '_neg'
                negated = False

            if w in StopWords():
                negated = False
                continue

            w = st.stem(w)
            if w: retVal.append(w)


    # Get url base
    match = re.search('(?:[^\.]*\.)*(.*)\.(?:com|org|gov|net|co|tv|biz)', link)
    if match:
        base = match.groups(0)
        retVal.append('urlbase-%s' % base)
    else:
        pass
        #print url
        #print 'link: ', link
        #print 'base: ', 'COULDNT'
        #print


    print '\t', retVal
    print

    return retVal



def split_hashtag(word):

    """
    split_hashtag()

    Purpose: Try to build list of words in hashtag concatentation
             ( ex. "#CurrentEvents"  ->  ["Current", "Events"] )

    @param  word.   A string beginning with a "#"
    @return         A list of words of the tokenized hashtag word
    """

    full = [word]

    # Assume CamelCase
    toks = re.findall('([A-Z][a-z]+|[0-9]+)', word)
    if toks: return full + toks

    # Greedy word split
    # TaskB/etc/dictionary.txt

    # Give up
    return full



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
            negated = False
            retVal.append('')

        # User mention
        elif word[0] == '@':
            retVal.append('@someuser')

        # Hashtag
        elif word[0] == '#':
            # Split hashtag word
            print '\t', word
            toks = split_hashtag(word)
            HT_negated = False
            for w in toks:
                w = st.stem(w.lower())
                w = w.lower()

                if isNegation(w):
                    HT_negated = not HT_negated
                else:
                    if HT_negated:
                        w = w + '_neg'
                        negated = False

                retVal.append(w)

        # URL
        elif isUrl(word):
            data = normalize_url(word)
            for w in data:
                retVal.append(w)

        # Negation
        elif isNegation(word):
            negated = not negated
            retVal.append(word)

        # Emoticon
        elif emoticon_type(word):
            #if negated: word = word + '_neg'
            retVal.append(word)

        # Simple word
        else:
            if not word: continue

            #if word in StopWords(): continue

            word = word.lower()
            word = word.strip(string.punctuation)
            word = st.stem(word)

            if negated:
                word = word + '_neg'
                negated = False
            retVal.append(word)

    #return set(retVal)
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