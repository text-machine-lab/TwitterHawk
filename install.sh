
#
#  Willie Boag
#
#  Biscuit - install.sh
#

# Not implemented yet
#echo "Sorry. install.sh not implemented yet"
#exit

# Obtain ark_tweet_nlp tool
cd tools
git clone https://github.com/ianozsvald/ark-tweet-nlp-python.git
cd ..

# Create virtual environment

# Require BISCUIT_DIR

# Install python dependencies
pip install numpy scipy scikit-learn
pip install nltk
pip install BeautifulSoup
pip install twitter
pip install pyenchant

