#-------------------------------------------------------------------------------
# Name:        train.py
#
# Purpose:     Train an svm
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import sys
import os
import glob
import argparse
import cPickle as pickle
from collections import defaultdict


# Scikit-learn
import numpy as np
from sklearn.feature_extraction import DictVectorizer

from sklearn.svm import LinearSVC
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import SGDClassifier

# My code
from note import Note, find_target
from tweet import Tweet, labels_map
from download import topic_search
from taskc_features.features import FeaturesWrapper

from TaskB.code.predict import predict_full_tweet_sentiment


BASE_DIR = os.path.join(os.getenv('BISCUIT_DIR'),'TaskC')




def main():

    """
    main()

    Purpose: This program builds an SVM model for Twitter classification
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("-t",
        dest = "txt",
        help = "The files that contain the training examples",
        default = os.path.join(BASE_DIR, 'data/topics.txt')
    )

    parser.add_argument("-m",
        dest = "model",
        help = "The file to store the pickled model",
        default = os.path.join(BASE_DIR, 'models/C-awesome')
    )

    # Parse the command line arguments
    args = parser.parse_args()

    # Decode arguments
    txt_files = glob.glob(args.txt)
    model_path = args.model


    # Cannot train on empty list
    if not txt_files:
        print 'no training files :('
        exit(1)


    # Read the data into a Note object
    notes = []
    for txt in txt_files:
        note_tmp = Note()
        note_tmp.read(txt)
        notes.append(note_tmp)

    # Get data from notes
    X = []
    Y = []
    for n in notes:
        X += zip(n.getTweets(), n.getTopics())
        Y += n.getLabels()

    # Organize data into list of tweets
    groups = defaultdict(lambda:[])
    for twt,topic in X:
        groups[topic].append( ' '.join(twt[2]) )

    # Look at data (grouped by topics)
    verbosity = 0
    for topic,data in groups.items():
        if verbosity > 1: print '\n\n'
        if verbosity > 0: print topic
        for text in data:
            if verbosity > 1: print '\t', text
            if verbosity > 1: print

    """

    #topic = 'bill murray'

    # Build a classifier for each topic
    for topic in groups.keys():

        print 'topic: ', topic

        # Get tweets about topic
        tweets = topic_search(topic, count=5000)

        print 'len(tweets): ', len(tweets)
        if len(tweets) < 50:
            print '\n\tToo few training examples'
            continue

        # Get silver standard annotation for training model
        text = [ twt['text'] for twt in tweets ] 
        data = sentiment(text)

        # Format silver annotations for training
        X = []
        Y = []
        for text,label in data:
            start,end = find_target(text, topic)
            X.append( (start,end,text.split() ) )
            Y.append(label)

        '''
        # Separate positive and negative examples
        positive = []
        negative = []
        for text,label in data:
            if label == 'positive':
                positive.append(text)
            if label == 'negative':
                negative.append(text)

        # Display some data
        print len(data)
        print 'positive: ', len(positive)
        print 'negative: ', len(negative)
        for tweet in positive[:5]:
            print tweet
            print '-' * 80
        '''

        model = model_path + '-' + topic.replace(' ','-')
        train_topic_sentiment_classifier(X, Y, model)

    """



def train_topic_sentiment_classifier(X, Y, model_path=None):

    # Extract features
    feat_obj = FeaturesWrapper()
    X = extract_features(X, feat_obj)

    # Vectorize feature dictionary
    vec = DictVectorizer()
    X = vec.fit_transform(X)

    # Vectorize labels
    labels = [ labels_map[y] for y in Y ]
    Y = np.array(  labels  )

    clf = LinearSVC(C=0.1)
    #clf = svm.SVC(C=0.1, gamma=10.0)
    #clf = LogisticRegression(C=1000.0)
    #clf = SGDClassifier(penalty='elasticnet',alpha=0.001, l1_ratio=0.85, n_iter=1000,class_weight='auto')
    clf.fit(X, Y)

    # Save model
    print 'train_vectorized: ', model_path
    if model_path:
        with open(model_path+'.dict' , 'wb') as f:
            pickle.dump(vec, f)

        with open(model_path+'.model', 'wb') as f:
            pickle.dump(clf, f)

    # return model
    return vec, clf




def extract_features(X, feat_obj=None):
    # Data -> features
    if feat_obj == None: feat_obj = FeaturesWrapper()
    return feat_obj.extract_features(X)





# Proxy for classification
def sentiment(text_list):

    # Preprocess text
    X = []
    for x in text_list:
        try:
            x = x.decode('utf-8','ignore')
            X.append(x)
        except UnicodeEncodeError, e:
            pass

    # Predict sentiment
    labels = predict_full_tweet_sentiment(X)

    return zip(X, labels)




def heuristic_sentiment(text_list):

    def heuristic_predict(text):

        text = text.lower()

        if '!' in text: return 'positive'

        # Positive?
        pos_words = ['great', 'good', 'awesome', 'incredible', 'happy', 'cool']
        for w in pos_words:
            if 'not ' + w in text: return 'negative'
            if          w in text: return 'positive'

        # Negative?
        neg_words = ['terrible', 'mad', 'pissed', 'upset', 'awful', 'angry']
        for w in neg_words:
            if 'not ' + w in text: return 'positive'
            if          w in text: return 'negative'

        # Neutral
        return 'neutral'


    # predict
    labels = [ heuristic_predict(text) for text in text_list ]

    return zip(text_list, labels)




if __name__ == '__main__':
    main()
