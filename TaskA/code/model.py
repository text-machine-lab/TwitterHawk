#-------------------------------------------------------------------------------
# Name:        model.py
#
# Purpose:     Extract features
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


from taska_features.features import features_for_tweet



labels_map = dict(positive=0, negative=1, neutral=2)
reverse_labels_map = { v:k for k,v in labels_map.items()}




def extract_features(data):

    """
    Model::extract_features()

    Purpose: Generate features for the input data

    @param data.  A list of data points
    @return       A list of feature dictionaries
    """

    # list of feature dictionaries
    feats_map = lambda t: features_for_tweet(t)
    feats = map( feats_map, data )

    return feats




def extract_labels(notes):

    """
    Model::extract_labels()

    @param notes. A list of note objects that store the tweet data
    @return       A list of integer classifications
    """

    # labels - A list of list of concepts (1:1 with data)
    labels = []
    for note in notes:
       labels += note.conlist()

    # Convert labels from strings to ints (ex. "positive" -> 0)
    classifications = [ labels_map[l] for l in labels ]

    return classifications




def convert_labels(note, labels):

    """
    Model::convert_labels()

    @param note.   A Note object that contains the prediction data
    @param labels. numpy.array of labels predicted by classifier

    Purpose: translate labels_list into a readable format
           ex. change all occurrences of 0 -> 'positive'
    """

    # Convert: numpy.array -> list
    labels = list(labels)

    # one-to-one correspondence between words in 'data' and predictions in 'labels'
    classifications = [ reverse_labels_map[l] for l in labels ]

    return classifications



