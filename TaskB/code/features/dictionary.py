#-------------------------------------------------------------------------------
# Name:        dictionary.py
#
# Purpose:     Interface to dictionary in order split stream of characters
#              into words.
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import os


BASE_DIR = os.path.join(os.getenv('BISCUIT_DIR'),'TaskB')



# For development: allow module to be run-able
def main():

    # Build dictionary
    filename = os.path.join(BASE_DIR, 'etc/dictionary.txt')
    build_dictionary(filename)

    # Split stream
    stream = 'angelinvestor'
    words = split_stream(stream)

    print words




# Dictionary of emoticons
_dictionary = set([])



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
        _dictionary.add(line)




def split_stream(word):

    """
    split_stream()

    Purpose: Given a stream of characters, split it into a list of words

    @param word.  A stream of characters
    @return       A list of valid words.
    """

    print _dictionary

    return [word]




if __name__ == '__main__':
    main()
else:
    # Build dictionary
    filename = os.path.join(BASE_DIR, 'etc/dictionary.txt')
    build_dictionary(filename)
