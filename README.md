Biscuit
=======

Classifiers for SemEval 2015 Tasks.


SemEval 2015       http://alt.qcri.org/semeval2015/task10/




Installation

    Required python modules:

        - numpy
        - scikit-learn
        - scipy


    Must create a BISCUIT_DIR environment variable.


    Get a dictionary from http://www.math.sjsu.edu/~foster/dictionary.txt

    Eventually, may use trie for Hashtag Segmentation dictionary lookup.




Usage

    N/A




Task A - Contextual Polarity Disambiguation

    Currently, uses normalized unigrams & lexicon features for F1 of 



Task B - Message Polarity Classification

    Currently, uses normalized unigrams for an F1 of 57.6.

    Working on: 

        - Hashtag Segmentation
        - POS tagging & IOB chunking (with twitter_nlp)
        - meta data features of tweets (ex. retweet count)



Task C - Topic-Based Message Polarity Classification

    N/A


Task D - Detecting Trends Towards a Topic

    N/A


Task E - Determining strength of association of Twitter terms with positive sentiment

    N/A


