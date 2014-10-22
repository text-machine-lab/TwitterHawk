#-------------------------------------------------------------------------------
# Name:        note.py
#
# Purpose:     Internal representation of file
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


from collections import defaultdict

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

        print '\t\t', dict(labels)



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



    def getTweets(self):

        """
        Note::getLabels()

        Purpose: Return a list of 3-tuples to classify.

        Format: A 3-tuple has a:
            1) begin index
            2)   end index
            3) sentence
        """

        # Get each (begin,end,sentence) triple
        retVal = []
        for tweet in self.tweets:
            retVal.append( (tweet.begin, tweet.end, tweet.sent) )

        return retVal



    def getLabels( self ):

        """
        Note::getLabels()

        Purpose: Return a list labels for the tweets
        """

        return [  tweet.label  for  tweet  in  self.tweets  ]



    def getIDs( self ):

        """
        Note::getIDs()

        Purpose: Return a list status IDs for the tweets
        """

        return [  tweet.sid  for  tweet  in  self.tweets  ]




    def __iter__(self):

        """
        Note::__iter__()

        Purpose: Allow Note objects to be iterable.
        """

        return iter(self.tweets)
