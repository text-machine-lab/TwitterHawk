#-------------------------------------------------------------------------------
# Name:        note.py
#
# Purpose:     Internal representation of file
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


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

        with open(txt) as f:
            for line in f:
                # Ignore tweets that are ill-formatted
                try:
                    # Add tweet representation to the list
                    twt = Tweet(line)
                    self.tweets.append( twt )
                except BadTweetException, e:
                    continue



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




    def txtlist(self):

        """
        Note::txtlist()

        Purpose: Return a list of full text of tweets
        """

        # Get each (begin,end,sentence) triple
        retVal = []
        for tweet in self.tweets:
            retVal.append(tweet.sent)

        return retVal




    def conlist( self ):

        """
        Note::conlist()

        Purpose: Return a list labels for the tweets
        """

        retVal = []

        # Get each (begin,end,sentence) triple
        for tweet in self.tweets:
            retVal.append( tweet.label )

        return retVal




    def __iter__(self):

        """
        Note::__iter__()

        Purpose: Allow Note objects to be iterable.
        """

        return iter(self.tweets)
