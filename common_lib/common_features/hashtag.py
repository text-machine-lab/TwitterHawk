#-------------------------------------------------------------------------------
# Name:        hashtag.py
#
# Purpose:     Interface to dictionary in order split stream of characters
#              into words.
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import os,sys
import re
import string


# Add common-lib code to system path
sources = os.getenv('BISCUIT_DIR')
if sources not in sys.path: sys.path.append(sources)
from common_lib.read_config import enabled_modules


# Add trie module to path
trie_module = enabled_modules['hashtag']
if trie_module:
    print trie_module
    if trie_module not in sys.path: sys.path.append(trie_module)
    import patricia
    _dictionary = patricia.trie()
else:
    _dictionary = {}


# For development: allow module to be run-able
def main():

    # Build dictionary
    filename = os.path.join(enabled_modules['hashtag'], 'dictionary.txt')
    build_dictionary(filename)

    # Split stream
    htags = os.path.join(enabled_modules['hashtag'], 'examples.txt')
    with open(htags,'r') as f:
        for line in f:
            stream = line.strip()
            toks = split_hashtag(stream)
            print stream, '\t', toks



def build_dictionary(filename):

    """
    build_dictionary()

    Purpose: Build dictionary of words

    Side effect: Populate '_dictionary' with set of words
    """

    # Dictionary
    f = open( filename, 'r' )

    # Every line of the lexicon
    for line in f.readlines():

        line = line.strip()

        # skip blank lines
        if not line.split(): continue

        # Get word
        _dictionary[line] = 1




def split_stream(word):

    """
    split_stream()

    Purpose: Given a stream of characters, split it into a list of words

    @param word.     A stream of characters
    @return          A list of valid words.
    """

    word = word.strip('#').lower()
    toks = []

    # Greedy Algorithm: Longest legal match
    s = 0
    e = 0
    lind = None
    longest = None
    while e < len(word):
        # Capture leading numbers
        match = re.search('^([0-9]+)', word[s:])
        if match:
            num = match.group(1)
            toks.append(num)
            s += len(num)
            e += len(num)
            continue
        
        sub = word[s:e+1]

        # Longest legal word so far
        if sub in _dictionary:
            longest = sub
            lind = e
        
        # No more possible legal words
        if not _dictionary.isPrefix(sub):
            if longest != None:
                toks.append(longest)
                s = lind + 1
                e = lind + 1
                longest = None
                lind    = None
            else:
                toks.append(word[s])
                s += 1
                e  = s

        e += 1

    sub = word[s:e+1]
    if sub: toks.append(sub)

    return toks




def split_hashtag(word):

    """
    split_hashtag()

    Purpose: Try to build list of words in hashtag concatentation
             ( ex. "#CurrentEvents"  ->  ["Current", "Events"] )

    @param  word.   A string beginning with a "#"
    @return         A list of words of the tokenized hashtag word
    """

    # Acronym?
    if word.isupper(): return [word.strip('#').lower()]

    # Try CamelCase and return if exact match
    toks = re.findall('([A-Z][a-z]+|[0-9]+)', word)
    toks = [ t.lower() for t in toks ]
    if len(''.join(toks)) == len(word[1:]): return toks

    # Greedy word split
    normed = word.strip(string.punctuation)
    toks = split_stream(normed)
    return toks




if __name__ == '__main__':
    main()
else:
    # Build dictionary
    basename = enabled_modules['hashtag']
    if basename:
        filename = os.path.join(enabled_modules['hashtag'], 'dictionary.txt')
        build_dictionary(filename)
