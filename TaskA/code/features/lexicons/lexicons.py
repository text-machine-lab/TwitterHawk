#-------------------------------------------------------------------------------
# Name:        lexicons.py
# Purpose:     Interface for lexicon data
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


# Instantiate each lexicon interface
import EmotionLexicon, SubjectivityLexicon, SentimentLexicon, OpinionLexicon

lexHTS  = SentimentLexicon.SentimentLexicon('HashtagSentiment')
lexS140 = SentimentLexicon.SentimentLexicon('Sentiment140')
lexOpi  = OpinionLexicon.OpinionLexicon()
lexSubj = SubjectivityLexicon.SubjectivityLexicon()
lexEmo  = EmotionLexicon.EmotionLexicon()
