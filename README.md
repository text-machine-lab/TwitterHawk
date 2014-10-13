Biscuit
=======

Classifiers for SemEval 2015 Tasks.


SemEval 2015       http://alt.qcri.org/semeval2015/task10/




Installation

    Required python modules:

        - numpy
        - scikit-learn
        - scipy
        - nltk
        - nose
        - BeautifulSoup
        - twitter


    Must create a BISCUIT_DIR environment variable.


    The system knows which advanced features to include from reading $BISCUIT_DIR/config.txt


    Hashtag Segmentation
        - Hashtag segmentation requires a dictionary of legal words.
        - Online dictionary: https://raw.githubusercontent.com/eneko/data-repository/master/data/words.txt
        - Store this file in $BISCUIT_DIR/common-lib/features/hashtag/words.txt

        - Trie for hashtag segmentation from https://github.com/fnl/patricia-trie




Usage

    N/A




Task A - Contextual Polarity Disambiguation

    Best F1: .87



Task B - Message Polarity Classification

    Best F1: .67



Task C - Topic-Based Message Polarity Classification

    N/A


Task D - Detecting Trends Towards a Topic

    N/A


Task E - Determining strength of association of Twitter terms with positive sentiment

    N/A


