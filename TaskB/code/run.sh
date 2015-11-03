python train.py

python predict.py -i ../data/twitter-test-2015-b.txt

cd /data1/wboag/twitterhawk/TwitterHawk/TaskB/data/C/official_scoring
perl score-semeval2015-task10-subtaskB.pl ../../predictions/twitter-test-2015-b.txt

#python evaluate.py -e
