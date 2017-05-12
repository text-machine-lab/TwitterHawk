

import os
import sys
from collections import defaultdict

import spell


# Add common-lib code to system path
sources = os.getenv('BISCUIT_DIR')
if sources not in sys.path: sys.path.append(sources)
from common_lib.common_features import utilities
from common_lib.read_config import enabled_modules


# Global resources
_tf = defaultdict(lambda:0)
_df = defaultdict(lambda:0)


# Empirically computed stop words (high entropy)
stop_words = set()
#stop_words = utilities.stop_words

#'''
# Read hard-coded stop words
with open(enabled_modules['stopwords'],'r') as f:
    for line in f.readlines():
        if line != '\n':
            stop_words.add(line.strip('\n'))
#'''


def doc_freq(word):
    return _df[word]




def tokenize(tagger, text):
    if tagger:
        tagger.update(text)
        all_toks = [ tagger.tokens(t) for t in text ]
    else:
        all_toks = [ t.split()        for t in text ]
    normed = all_toks
    #normed = [ utilities.normalize_phrase_TaskB(toks) for toks in all_toks ]
    #normed = [ spell.correct_spelling(toks) for toks in normed ]
    return normed



def _build_dictionary(tagger, data_path):

    global _tf, _df


    label_counts = defaultdict(lambda:0)
    all_data = set()
    for fname in os.listdir(data_path):

        fpath = os.path.join(data_path, fname)
        with open(fpath, 'r') as f:

            # Accumulate list of tweets (just text)
            for line in f.readlines():
                label = line.split('\t')[2]
                text = '\t'.join(line.split('\t')[3:]).strip('\n')
                text = text.decode('ascii','ignore')

                # Unssen tweet?
                if (label,text) not in all_data: label_counts[label] += 1

                all_data.add((label,text))


    # Fine grained analysis
    df_by_labels = defaultdict(lambda:defaultdict(lambda:0))

    # List of "documents" of tokens
    all_text = [ data[1] for data in all_data ] 
    all_toks = tokenize(tagger,all_text)
    all_data = [ (data[0],text) for (data,text) in zip(all_data,all_toks) ]
    for label,doc in all_data:

        # Frequency of each word
        freqs = defaultdict(lambda:0)
        for tok in doc:
            freqs[tok.lower()] += 1

        # Count term frequencies and document frequencies
        for t,f in freqs.items():
            _tf[t] += f
            _df[t] += 1
            df_by_labels[t][label] += 1

    '''
    # Detect semantically ambiguous words
    for k,v in sorted(df_by_labels.items(),key=lambda t:sum(t[1].values())):
        if similar(v, label_counts):
            stop_words.add(k)
            #print '%-15s' % k , '\t', display_percents(v, label_counts)
    '''

    '''
    # Output list of data-defined stop words
    with open('/data1/nlp-data/twitter/tools/stop-words.txt','w') as f:
        for w in stop_words:
            print >>f, w
    '''
    #exit()


def similar(v, labels):

    percents = {}
    for label in labels:
        percents[label] = (100.0 * v[label]) / labels[label]

    # Determine if all words occur with roughly the same percentages
    keys = { i:label for i,label in enumerate(['positive','negative','neutral'])}
    for i in range(len(keys)):
        for j in range(i):
            s1 = percents[keys[i]]
            s2 = percents[keys[j]]
            if abs(s1 - s2)/(s1+.00001) > 0.15: return False

    #return False
    return True


def display_percents(v, labels):

    retVal = []

    for label in labels:
        score = (100.0 * v[label]) / labels[label]
        retVal.append(label[:3] + ': %.5s' % str(score) )
        #retVal.append(v[label])

    return retVal



if __name__ == '__main__':

    # Add common-lib code to system path
    sources = os.getenv('BISCUIT_DIR')
    if sources not in sys.path: sys.path.append(sources)
    from common_lib.read_config                  import enabled_modules
    from common_lib.common_features.ark_tweet    import ark_tweet

    if enabled_modules['ark_tweet']:
        tagger = ark_tweet.ArkTweetNLP()
    else:
        tagger = None

    _build_dictionary(tagger, '/data1/nlp-data/twitter/data/etc')

    # Explicitly delete cache
    del(tagger.cache)

