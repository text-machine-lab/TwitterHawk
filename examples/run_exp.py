from __future__ import print_function

import csv

import sys
sys.path.append('/home/ppotash/_From Bell, Eric/ark-twokenize-py/')
sys.path.append('/home/ppotash/semeval15/Biscuit/TaskB/code')
from predict import TwitterHawk
from twokenize import tokenizeRawTweetText
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from sumy.models.dom._sentence import Sentence
from sumy.models.dom._paragraph import Paragraph
from sumy.models.dom._document import ObjectDocumentModel
from os import listdir
import numpy as np
from exp_runner import UnsupervisedExpRunner
from utils import get_tweet_embedding

class TwokenizeWrapper(object):
    def to_words(self, in_text):
        return tokenizeRawTweetText(in_text)

def get_lexrank(tweets):
    sens = [Sentence(t, TwokenizeWrapper()) for t in tweets]
    tweet_document = ObjectDocumentModel([Paragraph(sens)])
    LANGUAGE = "english"
    stemmer = Stemmer(LANGUAGE)
    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    SENTENCES_COUNT = len(sens)
    lex_ranked = summarizer(tweet_document, SENTENCES_COUNT)
    if len(sens) != len(lex_ranked):
        print('lr error')
    return [lex_ranked[s] for s in sens]


def load_hashtag(htf, th):
    label_map = {'9':1, '1':2}
    tweets = []
    labels = []
    for line in open('../data/cleaned_tweets/' + htf).readlines():
        line_split = line.strip().split('\t')
        tweets.append(line_split[:2])
        if len(line_split) == 3:
            labels.append(label_map[line_split[2]])
        elif len(line_split) == 2:
            labels.append(0)
        else:
            print('error', line_split)

    lex_ranks = get_lexrank([t[1] for t in tweets]) # We want just the tweet text! not a list of tweet id and text!
    sents = th.predict(tweets, predict_type='probs')

    Y = np.array(labels)
    X_lex = np.array(lex_ranks)
    X_neg = sents[:, 1]
    X_pos = sents[:, 0]

    X_embed = np.array([get_tweet_embedding(t, tokenizeRawTweetText) for tid, t in tweets])

    return {'X_lex':X_lex, 'X_neg':X_neg, 'X_pos':X_pos, 'Y':Y, 'X_embed':X_embed}

if __name__ == '__main__':

    compare_labels = [(1, 0), (2, 1), (2, 0)]

    # you can provide the `measure` argument, by default `measure` is lambda a, b : np.linalg.norm(a) > np.linalg.norm(b)
    runner_lex = UnsupervisedExpRunner(compare_labels=compare_labels)
    runner_neg = UnsupervisedExpRunner(compare_labels=compare_labels)
    runner_pos = UnsupervisedExpRunner(compare_labels=compare_labels)

    runner_lex_neg = UnsupervisedExpRunner(compare_labels=compare_labels)
    runner_lex_pos = UnsupervisedExpRunner(compare_labels=compare_labels)


    th = TwitterHawk('/home/ppotash/semeval15/Biscuit/TaskB/models/trained.model')

    ht_files = listdir('../data/cleaned_tweets')
    # label_map = {'9':1, '1':2}


    for htf in ht_files:
        print(htf)

        # X_lex, X_neg, X_pos, Y = load_hashtag(htf, th)
        data_dict = load_hashtag(htf, th)
        X_lex, X_neg, X_pos, Y = data_dict['X_lex'], data_dict['X_neg'], data_dict['X_pos'], data_dict['Y']

        runner_lex.run_exp(htf, X_lex, Y)
        runner_neg.run_exp(htf, X_neg, Y)
        runner_pos.run_exp(htf, X_pos, Y)

        runner_lex_neg.run_exp(htf, np.concatenate([X_lex[:, np.newaxis], X_neg[:, np.newaxis]], axis=1), Y)
        runner_lex_pos.run_exp(htf, np.concatenate([X_lex[:, np.newaxis], X_pos[:, np.newaxis]], axis=1), Y)


    average = 'micro'
    print('Average', average)
    print('lex:', runner_lex.get_results(average))
    print('neg', runner_neg.get_results(average))
    print('pos', runner_pos.get_results(average))
    print('lex neg', runner_lex_neg.get_results(average))
    print('lex pos', runner_lex_pos.get_results(average))
    # for exp_name, exp_runner in zip(
    #         ['lex', 'neg', 'pos', 'lex neg', 'lex pos'],
    #         [runner_lex, runner_neg, runner_pos, runner_lex_neg, runner_lex_pos]
    #     ):
    #     print('==============')
    #     print(exp_name)
    #     for ht, accuracy in exp_runner.get_results().items():
    #         print(ht, '\t', accuracy)
    #
    #     print('==============')


    # save the results
    filename_template = 'results_unsupervised_by_hashtags_{0}.csv'
    experiments = [
        ('lex', runner_lex), ('neg', runner_neg), ('pos', runner_pos),
        ('lex_neg', runner_lex_neg), ('lex_pos', runner_lex_pos),
    ]
    for ex_title, ex_runner in  experiments:
        ex_results = ex_runner.get_results()

        filename = filename_template.format(ex_title)
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            for ht, acc in ex_results.items():
                writer.writerow([ht, acc])

        print('Saved: ', ex_title, filename)

