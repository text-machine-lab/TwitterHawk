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
                    #print 'BAD TWEET: ', line.strip()
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
        for twt in self.tweets:
            #print
            #print twt.tweet
            #print twt.topic
            #print len(twt.tweet)

            start,end = find_target(twt.tweet, twt.topic)
            retVal.append(  (start,end,twt.tweet.split(' '))  )

            #if len(twt.topic.split()) > 1: exit()

        return retVal



    def getLabels( self ):

        """
        Note::getLabels()

        Purpose: Return a list labels for the tweets
        """

        return [  tweet.label  for  tweet  in  self.tweets  ]



    def getTopics( self ):

        """
        Note::getTopics()

        Purpose: Return a list topic for the tweets
        """

        return [  tweet.topic  for  tweet  in  self.tweets  ]



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




def find_target(text, topic):

    start = None
    end = None

    topic = topic.lower().split()
    cand = 0 # used for backtracking in multi-token topics
    tlength = len(topic)

    p = False #'Ramcharan Escaped' in text


    sentence = text.split()

    if p: print '\n'
    if p: print ' '.join(sentence)
    if p: print sentence
    if p: print 'topic: ', topic

    for i,tok in enumerate(sentence):

        if p: print i, tok
        if p: print '\t', topic[cand], tok.lower()

        # Does candidate match beginning of topic?
        # Note: Cannot achieve perfect matches because of false matches
        if topic[cand] in tok.lower():

            if p: '\t\t', cand, tok

            # Beginning of new candidate?
            if cand == 0:
                start = i

            # Full match?
            if cand == tlength - 1:
                end = i
                break

            # match of one token
            cand += 1

        else:

            # Interesting: Moore vs. Mealy sequence matching
            #   ex. topic: "bill murray", text: "i love bill bill murray"
            #   first bill changes cand & it misses correct sequence
            # Solution: backtrack as far back as need to
            j = i
            while (cand > 0) and (topic[cand] == sentence[j-1]):
                cand -= 1
                j    -= 1


    if end == None:
        print topic
        print text

    # Ensure found token
    assert (end != None), "could not find token"

    return start,end

