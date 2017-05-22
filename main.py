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

from queue import Queue

# ================GLOBALS===============

queue_name = 'twitter_topic_feed'

DEBUG = False
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

# printer debugger
def dPrint(input_str):
	global DEBUG
	if DEBUG:
		print("DEBUG PRING: {}".format(input_str))



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

# function will be on single thread and load all the data into a single
# queue that I will create pika doesn't allow thread
# what I can do is put the sentiment analysis on multiple threads
# reading from a thread safe queue that I create
def load_worker():

	start = time.time()

	

	tweet = ''

	method_frame, properties, body = next(channel.consume(queue_name))

	try:
		encoded_line = body.decode('unicode_escape', 'ignore')
		tweet = encoded_line.encode('utf8').decode('ascii', 'ignore') # small unicode errors rise without this

	# here just to see what time of encoding raises an error so it can be fixed
	except Exception as e:
		with open('log.txt', 'a') as file:
			file.write(body.decode('utf-8'))
		print('Error at decoding: {}'.format(e))

	# Acknowledge the message was recieved
	channel.basic_ack(method_frame.delivery_tag)

	''' This might be fixable if we load on a single thread and do the sentiment(heavier processor usage)
	in a few other threads, as time time to load it into a queue is smaller then the sentiment time
	'''


	# Cancel the consumer and return any pending messages
	# try:													# sort of useless pika doesn't support threading... look for a hack
	# 	requeued_messages = channel.cancel()
	# except IndexError as e:									# which is why this error is here
	# 	print("Thread lock may have happened: {}".format(e))
	
	# print("Program took {} time to run".format(time.time()- start))

	return tweet


q = Queue(maxsize=6000)
def queue_loader_worker():
	print('Thread starting loading data into queue...')
	while True:
		
		if not q.full():
			
			q.put(load_worker()) # grad from the message queue server and get it ready to do sentiment analysis
			# print('data now in queue')


# temporary and for the purpose of debugging
def mean_sentiment_worker():
	print('Thread starting waiting for right time...')
	while True:
		if datetime.datetime.now().second == 0 or datetime.datetime.now().second == 30:
			global pos_data_analysis, neg_data_analysis

			print('==========================')
			print('pos mean: {} with count {}'.format(mean(pos_data_analysis), len(pos_data_analysis)))
			print('neg mean: {} with count {}'.format(mean(neg_data_analysis), len(neg_data_analysis)))
			print('==========================')
			pos_data_analysis = []
			neg_data_analysis = []
			time.sleep(1)



# here is will be ok to keep multiple threads, since Queue is threadsafe
def sentiment_worker(thread_name):
	print("Starting {}...".format(thread_name))
	while True:
		# print(q.empty())
		if not q.empty():
			data = q.get()
			sentiment = nlp.get_sentimentVals(data)

			if sentiment > 0:
				pos_data_analysis.append(sentiment)

			elif sentiment < 0:
				neg_data_analysis.append(sentiment)

def check_q():
	while True:
		global q
		if q.empty(): dPrint('Queue is empty')
		elif q.full(): dPrint('Queue is full')
		time.sleep(1)




def livegraph():
	pass


def nlp_worker():

	#ignore the neutral since most are facts and news
	#remember to add them to the total later down the road

	worker_num = 'Thread 1'

	while True:
		sentiment = nlp.get_sentimentVals(get_tweets(worker_num))


def animate():
	global pos_data_analysis, neg_data_analysis


def main():

	# t1 = Thread(target=nlp_worker)
	# t2 = Thread(target=nlp_worker)
	# t1.daemon = True
	# t2.daemon = True
	# t1.start()
	# t2.start()


	# This section turns loads the threads functions

	# q_worker = Thread(target=nlp_worker)
	q_loader_worker = Thread(target=queue_loader_worker)
	q_checker = Thread(target=check_q)
	mean_print = Thread(target=mean_sentiment_worker)


	# add a thread that checks the time adds the data to a 


	threads = [q_loader_worker, q_checker, mean_print]

	for i in range(2):
		threads.append(Thread(target=sentiment_worker, args=('Sentiment worker #{} starting...'.format(i+1),)))

	# daemon makes sure that each thread stops if and when the main thread stops

	for thread in threads:
		thread.daemon = True
		thread.start()


	# now instead of this crazy loop make it update ever few minutes and put it on the graph

	while True:
		time.sleep(1)




if __name__ == '__main__':
	main()