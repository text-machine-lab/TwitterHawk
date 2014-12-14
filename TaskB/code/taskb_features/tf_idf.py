

import os
import sys
from collections import defaultdict

import spell


# Add common-lib code to system path
sources = os.getenv('BISCUIT_DIR')
if sources not in sys.path: sys.path.append(sources)
from common_lib.common_features import utilities



# Global resources
_tf = defaultdict(lambda:0)
_df = defaultdict(lambda:0)




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

    all_text = set()
    for fname in os.listdir(data_path):

        fpath = os.path.join(data_path, fname)
        with open(fpath, 'r') as f:

            # Accumulate list of tweets (just text)
            for line in f.readlines():
                text = '\t'.join(line.split('\t')[3:]).strip('\n')
                text = text.decode('ascii','ignore')
                all_text.add(text)

    # List of "documents" of tokens
    all_toks = tokenize(tagger,all_text)
    for doc in all_toks:

        # Frequency of each word
        freqs = defaultdict(lambda:0)
        for tok in doc:
            freqs[tok] += 1

        # Count term frequencies and document frequencies
        for t,f in freqs.items():
            _tf[t] += f
            _df[t] += 1

    #special = map(lambda tup:tup[0], filter(lambda tup:tup[1]==1, _df.items()))
    #for k in special: print k





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

    _build_dictionary(tagger, os.path.join(os.getenv('BISCUIT_DIR'),'TaskB/etc/data'))

    # Explicitly delete cache
    del(tagger.cache)

