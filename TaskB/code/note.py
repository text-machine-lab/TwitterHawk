#-------------------------------------------------------------------------------
# Name:        note.py
#
# Purpose:     Internal representation of file
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------

from collections import defaultdict
import os


from tweet import Tweet, BadTweetException


class Note:

    def __init__(self):
        """
        Note::Constructor
        """
        self.tweets = []


    def read(self, txt):
        """
        Note::read()

        @param txt. A filename that stores a series of tweets.

        Purpose: Read the file and store all tweets
        """
        labels = defaultdict(lambda:0)
        with open(txt) as f:
            for line in f:
                # Ignore tweets that are ill-formatted
                try:
                    # Add tweet representation to the list
                    twt = Tweet(line)
                    self.tweets.append( twt )
                    labels[twt.label] += 1
                except BadTweetException, e:
                    continue

        # Display info about where data is coming from
        if 'TwitterHawk' in txt:
            print '\t\treading file: ', txt[txt.index('TwitterHawk')+12:]
        else:
            print '\t\treading_file', txt
        print '\t\tlabels count: ', dict(labels)
        print



    def write(self, txt, labels):

        """
        Note::write()

        @param txt.    A filename that to write tweets to
        @param labels. A list of classifications for the tweet phrases

        Purpose: Write the concept predictions to a given file
        """

        with open(txt, 'w') as f:
            for tweet, lab in zip(self.tweets, labels):
                tweet.label = lab
                print >>f, tweet



    def text_list(self):

        """
        Note::text_list()

        Purpose: Return a list of full text of tweets
        """

        return [  tweet.sent  for  tweet  in  self.tweets  ]



    def label_list( self ):

        """
        Note::label_list()

        Purpose: Return a list labels for the tweets
        """

        return [  tweet.label  for  tweet  in  self.tweets  ]



    def sid_list( self ):

        """
        Note::sid_list()

        Purpose: Return a list status IDs for the tweets
        """

        return [  tweet.sid  for  tweet  in  self.tweets  ]


