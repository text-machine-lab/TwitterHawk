TwitterHawk
=======

Classifiers for SemEval 2015 Tasks.


SemEval 2015       http://alt.qcri.org/semeval2015/task10/




Installation

    Install of these python modules via pip:

        - nltk
        - pyenchant
        - numpy
        - BeautifulSoup
        - twitter
        - scikit-learn

        - scipy
        - nltk
        - nose


    Must create a BISCUIT_DIR environment variable.

        - Will hopefully be eliminated soon.


    Install the ark_tweet_nlp project for tokenization of tweets

        - git clone https://github.com/ianozsvald/ark-tweet-nlp-python.git
        - Set the config file to refer to the directory that you just cloned



Task B

    $ cd ./TaskB/code
    $ python train.py      # takes about 70s for me
    $ python predict.py    # takes about 30s for me



W. Boag, P. Potash, A. Rumshisky. TwitterHawk: A Feature Bucket Approach to Sentiment Analysis, In Proceedings of the 9th international workshop on Semantic Evaluation Exercises (SemEval-2015), June 2015, Denver, Colorado, USA.
http://www.cs.uml.edu/~wboag/research/publications/wboag-twitterhawk.pdf
