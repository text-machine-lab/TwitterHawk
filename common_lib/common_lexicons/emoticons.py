#-------------------------------------------------------------------------------
# Name:        emoticons.py
#
# Purpose:     Detect emoticons in words
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import os
import sys

# Add common-lib code to system path
sources = os.getenv('BISCUIT_DIR')
if sources not in sys.path: sys.path.append(sources)

from common_lib.read_config import enabled_modules




# For development: allow module to be run-able
def main():

    sentence = "I like the :) symbol."

    for word in sentence.split():

        etype = emoticon_type(word)

        print 'word:  ', word
        print 'etype: ', etype
        print ''




# Dictionary of emoticons
_emoticon_lexicon = {}




def build_lexicon(filename):

    """
    build_lexicon()

    Purpose: Build lexicon of emoticons

    Side effect: Populate 'emoticon_lexicon' with string -> label mappings.
    """

    # Emoticons table
    f = open( filename, 'r' )

    # Every line of the lexicon
    for line in f.readlines():

        # skip blank lines
        if not line.split(): continue

        # end of line has classification
        label = line.split()[-1]

        # Add every emoticon to the dictionary
        for word in line.split()[:-1]:
            _emoticon_lexicon[word] = label


    #print emoticon_lexicon



def emoticon_type(word):

    """
    emoticon_type()

    Purpose: Given a word, detect if it is an emoticon.

    @param word. A given word from a tweet
    @return      Either:
                    1) "positive", "negative", or "neutral" if emoticon
                    2) None                                 if no match
    """

    # Simple table lookup
    if word in _emoticon_lexicon:
        return _emoticon_lexicon[word]
    else:
        return None




if __name__ == '__main__':

    main()

else:

    # Build dictionary of emoticons
    base_dir = enabled_modules['lexicons']
    if base_dir:
        filename = os.path.join(base_dir, 'emoticons.txt')
        if os.path.exists(filename):
            build_lexicon(filename)
