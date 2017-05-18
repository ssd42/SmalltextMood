# sentiment analysis algorithm
from nltk import tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer




# prints out the sentiment of on the given string (utf-8 or ascii needed)
def analyze_text(text):
	# initializa the algorithm obj
	sid = SentimentIntensityAnalyzer() 

	#NOTE
	# in order to optimize time might have it loop here so sid 
	# wont have to be initialized everytime

	print("Analysis on the line: {}".format(text))
	ss = sid.polarity_scores(text)
	for k in sorted(ss):
		print('Sentiment:{}, Value:{}, '.format(k, ss[k]))


# same thing as above but instead of printing it returns the vals
def get_sentimentVals(text):

	sid = SentimentIntensityAnalyzer()
	ss = sid.polarity_scores(text)

	# available are compound/pos/neu/neg
	# get compound
	return ss['compound']

def mean(alist):
	mean_val = 0
	for val in alist:
		mean_val+=val
	return abs(mean_val/len(alist))
	