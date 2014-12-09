#
# Fetch twitter data about a given topic
#
#
#


from interface_twitter import TwitterInterface, maxTweets


def main():

    # Create object that allows me to communicate with Twitter
    twobject = TwitterInterface(connect=True)

    '''
    # Get a particular friend's timeline
    tweets1 = twobject.statuses_user_timeline(screen_name="WilliamBoag"    , count=maxTweets)
    '''

    #tweets = topic_search('Bill Murray')
    tweets = topic_search('Shia Labeouf')

    for twt in tweets:
        print twt['text']
        print '-'*40


# Set of unique tweets
seen = set()
statuses = []
def accumulate_tweets(keyword, tweets):
    global seen, retVal
    for tweet in tweets:
        # Same tweet with different URLs do not count as different
        key =' '.join([w for w in tweet['text'].split() if ('http://' not in w)])
        key = key.lower()
        if (key not in seen) and (key[:2] != 'RT') and (keyword in key):
            statuses.append(tweet)
            seen.add(key)



def topic_search(keyword, count=500):

    # Create object to connet to Twitter
    twobject = TwitterInterface(connect=True)

    # Reset the accumulated tweets
    global statuses
    statuses = []

    # Search for tweets about topic
    search_results = twobject.search_tweets(q=keyword, count=maxTweets)
    accumulate_tweets(keyword, search_results['statuses'])

    while len(statuses) < count:
        print '\t', len(statuses)
        try:
            # Follow pointer to more results
            next_results = search_results['search_metadata']['next_results']
            kwargs = dict([kv.split('=') for kv in next_results[1:].split('&')])
            kwargs['count'] = maxTweets
            kwargs[  'q'  ] = keyword

            # Get more tweets
            #print kwargs
            search_results = twobject.search_tweets(**kwargs)
            tweets = search_results['statuses']
            accumulate_tweets(keyword, tweets)
            #print '\t', len(tweets), len(statuses)
 
        except KeyError, e:
            break

    return statuses


if __name__ == '__main__':
    main()
