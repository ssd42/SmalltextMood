# import streamtweets
# import dataAnalysis
# import plotTweets
import json
from threading import Thread
import pika
import dataAnalysis as nlp
from numpy import mean
import time
import datetime

# ================GLOBALS===============

queue_name = 'twitter_topic_feed'

# ======================================



pos_data_analysis = []
neg_data_analysis = []


connection = pika.BlockingConnection()
channel = connection.channel()

# function initializes the twitter stream
# following a set of key words
# meant to  be run on a single thread
def stream(key_list):
	streamtweets.init_stream(key_list)


def load():
	pass


#function to get X messages from the queue
def get_tweets(threadname):
	tweet = ''

	method_frame, properties, body = next(channel.consume(queue_name))

	try:
		# json_line = json.loads(body.decode('unicode_escape', 'ignore')  )  #, strict=False)
		encoded_line = body.decode('unicode_escape', 'ignore')

		# following line gets rid of unicde characters which mess with the 
		# encoded_line =  json_line['text'].encode('utf-8', 'ignore')
	
		encoded_line = encoded_line.encode('utf8').decode('ascii', 'ignore') # small unicode errors rise without this


		# print("{} : {}".format(threadname, encoded_line))
		tweet = encoded_line
	except Exception as e:
		with open('log.txt', 'a') as file:
			file.write(body.decode('utf-8'))
		print('Error at decoding: {}'.format(e))


	# Acknowledge the message
	channel.basic_ack(method_frame.delivery_tag)

	# Cancel the consumer and return any pending messages
	try:													# sort of useless pika doesn't support threading... look for a hack
		requeued_messages = channel.cancel()
	except IndexError as e:									# which is why this error is here
		print("Thread lock may have happened: {}".format(e))
	
	return tweet


def stream_worker():
	pass


def livegraph():
	pass


def nlp_worker():

	#ignore the neutral since most are facts and news
	#remember to add them to the total later down the road

	worker_num = 'Thread 1'

	sentiment = nlp.get_sentimentVals(get_tweets(worker_num))

	if sentiment > 0:
		pos_data_analysis.append(sentiment)

	elif nlp.get_sentimentVals(get_tweets(worker_num)) < 0:
		neg_data_analysis.append(sentiment)

def main():

	# t1 = Thread(target=nlp_worker)
	# t2 = Thread(target=nlp_worker)
	# t1.daemon = True
	# t2.daemon = True
	# t1.start()
	# t2.start()


	while True:
		# nlp.get_sentimentVals(get_tweets('Thread1'))
		nlp_worker('Thread 1')
		if datetime.datetime.now().second == 0 or datetime.datetime.now().second == 30:
			global pos_data_analysis, neg_data_analysis
			print('pos mean: {}'.format(mean(pos_data_analysis)))
			print('neg mean: {}'.format(mean(neg_data_analysis)))
			print('========================')
			pos_data_analysis = []
			neg_data_analysis = []
			time.sleep(1)
		




if __name__ == '__main__':
	main()