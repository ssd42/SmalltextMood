# import json
from threading import Thread
import pika
import dataAnalysis as nlp
from numpy import mean
import time
import datetime

from queue import Queue

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

import matplotlib.dates as mdates
import matplotlib.ticker as mticker

# ================GLOBALS===============

queue_name = 'twitter_topic_feed'

DEBUG = False

pos_data_analysis = []
neg_data_analysis = []

pos_mean = []
neg_mean = []
# ======================================
# printer debugger
def dPrint(input_str):
	global DEBUG
	if DEBUG:
		print("DEBUG PRING: {}".format(input_str))

# establishing the pika connection to the server
connection = pika.BlockingConnection()
channel = connection.channel()
# =======================================================
# Animation code make own file later


# new test code


# ax1 = plt.subplot2grid((6,1), (0,0), rowspan=3, colspan=1)
# plt.title("Pos/Neg Sentiment")
# ax2 = plt.subplot2grid((6,1), (3,0), rowspan=3, colspan=1)
# plt.xlabel('Date')
# plt.ylabel('Sentiment')


# ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
# ax2.xaxis.set_major_locator(mticker.MaxNLocator(10))
# ax2.grid(True)





# style.use('fivethirtyeight')
# fig = plt.figure()
# ax1 = fig.add_subplot(2,1,1)
# ax2 = fig.add_subplot(2,1,2)

# plt.title("Pos/Neg Feeling based on tweet\'s")
# ax1.xaxis.set_data_interval(0, 10)
# ax1.yaxis.set_data_interval(0, 1)
first = True
max_size = 20


def graph_data():
	global pos_mean, neg_mean, max_size

	pos_graph_data = pos_mean[(-1*max_size):]
	neg_graph_data = neg_mean[(-1*max_size):]

	pxs = []
	pys = []
	for num, item in enumerate(pos_graph_data):
		pxs.append(num+1)
		pys.append(item)


	nxs = []
	nys = []

	for num, item in enumerate(neg_graph_data):
		nxs.append(num+1)
		nys.append(item)

	#clear the figure for new draw
	fig.clf()

	#set values
	style.use('fivethirtyeight')
	plt.locator_params(axis='x', nticks=1)

	ax1 = plt.subplot2grid((2,1),(0,0), rowspan=1, colspan=1)

	plt.title("Sentiment Analysis")
	plt.axis([0.0,max_size, 0.0,1.0])
	plt.ylabel('Pos')
	
	ax1.plot(pxs, pys, color='green')

	ax2 = plt.subplot2grid((2,1),(1,0), rowspan=1, colspan=1, sharex=ax1)

	plt.axis([0.0,max_size, 0.0,-1.0])
	plt.xlabel('Date')
	plt.ylabel('Neg')

	# ax2.set_xticklabels(timestamps)

	plt.subplots_adjust(bottom=0.2)
	plt.xticks(rotation=25)

	# ax=plt.gca()
	# xfmt = 
	# ax2.xaxis.set_major_formatter(md.DateFormatter('%Y-%m-%d %H:%M:%S'))
	
	
	ax2.plot(nxs, nys, color='red')



fig = plt.figure()
fig.suptitle('Waiting on initial data', fontsize=30, fontweight='bold')
def animate(i):
	if datetime.datetime.now().second in (0,30):
		graph_data()









# =======================================================


#===================================
# def animate_old(i):
# 	if datetime.datetime.now().second in (0,30):
# 		dPrint(datetime.datetime.now())
# 		global first
# 		global ax1
# 		global pos_mean, neg_mean


# 		print(pos_mean)

# 		#grab the last n items from the list and plot them (plotting for iregularities) can save later to db alll of them
# 		pos_graph_data = pos_mean[(-1*max_size):]

# 		xs = []
# 		ys = []
# 		if first:
# 			xs.append(0)
# 			ys.append(0)
# 			first = False

# 		for num, item in enumerate(pos_graph_data):
# 			xs.append(num+1)
# 			ys.append(item)

# 		ax1.clear()
# 		# ax2.clear()
# 		# plt.axis()
# 		# plt.axis([0.0,max_size, 0.0,1.0])
		

# 		# ax1.xaxis.set_data_interval(0, 10)
# 		# ax1.yaxis.set_data_interval(0, 1)

# 		plt.subplots_adjust(left=0.11, bottom=0.24, right=0.90, top=0.90, wspace=0.2, hspace=0)

# 		ax = plt.gca()
# 		ax.set_autoscale_on(False)
# 		ax1.plot(xs, ys)
# 		# ax2.plot(xs, ys)
#========================================================







# function initializes the twitter stream
# following a set of key words
# meant to  be run on a single thread
def stream(key_list):
	streamtweets.init_stream(key_list)


# Function no longer in use due to the channel cancelation
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
	# start = time.time()
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


def mean_into_lst():
	print('Loading means into lists')
	while True:
		if datetime.datetime.now().second == 58 or datetime.datetime.now().second == 28:
			global pos_mean, neg_mean, pos_data_analysis, neg_data_analysis

			pos_mean.append(mean(pos_data_analysis))
			neg_mean.append(mean(neg_data_analysis))
			pos_data_analysis = []
			neg_data_analysis = []
		
		time.sleep(1) # so it wont repeat more than once on each interval


# here is will be ok to keep multiple threads, since Queue is threadsafe
def sentiment_worker(thread_name):
	print("Thread {}...".format(thread_name))
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
	while DEBUG:
		global q
		if q.empty(): dPrint('Queue is empty')
		elif q.full(): dPrint('Queue is full')
		time.sleep(1)


def main():

	# This section turns loads the threads functions

	# q_worker = Thread(target=nlp_worker)
	q_loader_worker = Thread(target=queue_loader_worker)
	q_checker = Thread(target=check_q)
	# mean_print = Thread(target=mean_sentiment_worker)
	mean_print = Thread(target=mean_into_lst)

	# add a thread that checks the time adds the data to a 
	threads = [q_loader_worker, q_checker, mean_print]

	for i in range(2):
		threads.append(Thread(target=sentiment_worker, args=('Sentiment worker #{} starting...'.format(i+1),)))

	# daemon makes sure that each thread stops if and when the main thread stops
	for thread in threads:
		thread.daemon = True
		thread.start()

	ani = animation.FuncAnimation(fig, animate, interval=1000)
	plt.show()


if __name__ == '__main__':
	main()