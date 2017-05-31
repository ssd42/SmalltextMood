from threading import Thread
import pika
import dataAnalysis as nlp
import time
import datetime

from queue import Queue

from matplotlib import style

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

import numpy as np
from numpy import mean


# ================GLOBALS===============

queue_name = 'twitter_topic_feed'

DEBUG = False

pos_data_analysis = []
neg_data_analysis = []

pos_mean = []
neg_mean = []

temp_count = 0 #this is to include the nuetral tweets
total_count = []
total_count_mean = []

timestamps = []
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

first = True
max_size = 20


def graph_data():
	global pos_mean, neg_mean, total_count, total_count_mean
	global max_size

	# ==========================================
	# Data creation and loading
	# ==========================================

	# LINE to get the past n items out of the list mean

	pos_graph_data = pos_mean[(-1*max_size):]
	neg_graph_data = neg_mean[(-1*max_size):]
	t_count = total_count[(-1*max_size):]
	t_count_mean = total_count_mean[(-1*max_size):]

	tstamps = timestamps[(-1*max_size):]

	std_val = np.std(total_count, ddof=1)

	# load in the data for the pos graph
	pxs = []
	pys = []
	for num, item in enumerate(pos_graph_data):
		pxs.append(num)
		pys.append(item)

	# data for neg graph
	nxs = []
	nys = []

	for num, item in enumerate(neg_graph_data):
		nxs.append(num)
		nys.append(item)

	# ====================================================
	#	Alerts
	# ====================================================

	''' given the std deviation look for an extreem outlier 
	of the given data and if data deviates from for N time (suggestion of 2 mins)
	throw an alert. Now keep this focused on the data from the sheer amount of tweets 
	since as of now the change in sentiment has never deviated anything crazy (I also
	havent been monitoring it non stop)
	'''




	# ====================================================
	#	Graphing
	# ====================================================	

	#clear the figure for new draw
	fig.clf()

	#set values
	style.use('fivethirtyeight')
	plt.locator_params(axis='x', nticks=1)

	# pos grid
	ax1 = plt.subplot2grid((3,1),(0,0), rowspan=1, colspan=1)

	plt.title("Sentiment Analysis")
	plt.axis([0.0,max_size, 0.0,1.0])
	plt.ylabel('Pos')
	
	plt.xticks(pxs, " ") # shared by both ax1 & ax2
	
	


	# neg grid
	ax2 = plt.subplot2grid((3,1),(1,0), rowspan=1, colspan=1, sharex=ax1)

	plt.axis([0.0,max_size, 0.0,-1.0])
	# plt.xlabel('Date') #not needed for now
	plt.ylabel('Neg')

	# ax2.set_xticklabels(timestamps)

	plt.subplots_adjust(bottom=0.2)
	plt.xticks(rotation=25)


	# ax=plt.gca()
	# xfmt = 
	# ax2.xaxis.set_major_formatter(md.DateFormatter('%Y-%m-%d %H:%M:%S'))
	

	# bargraph grid for sample data size
	ax3 = plt.subplot2grid((3,1), (2,0), rowspan=1, colspan=1)


	plt.xlabel('Time \n\nStandard Deviation = {0:.2f}'.format(std_val))
	plt.ylabel('Total Tweets ')
	plt.subplots_adjust(bottom=0.2)
	plt.xticks(rotation=25)

	# plt.xticks(np.arange(0, 20, 1.0), rowspan=25)

	# small hardfix for the plot range (want to keep 0 a min)
	if len(total_count) > 0:
		plt.axis([0.0, max_size, min(total_count)*0.8, max(total_count)*1.1]) #	multiplication is to set a floor and ceiling	
	else:
		plt.axis([0.0, max_size, 0.0, 10])


	ax3.set_xticklabels(tstamps) #timestamps setting

	# this is for plotting the date later on
	loc = mticker.MultipleLocator(base=1.0) # this locator puts ticks at regular intervals of 1 (for timestamps)
	ax2.xaxis.set_major_locator(loc)
	ax3.xaxis.set_major_locator(loc)


	# legends
	ax1.plot(pxs, pys, color='green', label='pos ratio')
	ax2.plot(nxs, nys, color='red', label='neg ratio')
	ax3.plot(nxs, t_count, color='black', label='tweet count')
	ax3.plot(nxs, t_count_mean, color='orange', label='tweet mean')


	# plt.legend(bbox_to_anchor=[0.5,0.5], loc='bottom left', ncol=1, mode="expand", borderaxespad=0.) #legend setter
	ax1.legend(loc='upper left', fontsize='small')
	ax2.legend(loc='upper left', fontsize='small')
	ax3.legend(loc='upper left', fontsize='small')



# setting up the pre-screen before first batch of data pours in
fig = plt.figure()
fig.suptitle('Waiting on initial data', fontsize=30, fontweight='bold')
# FUNCAnimation
def animate(i):
	if datetime.datetime.now().second in (0,30):
		graph_data()

# =======================================================





# single thread streaming init
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
		if datetime.datetime.now().second == 58 or datetime.datetime.now().second == 28: #NOTE: not sure of this as is... i understand the extra time but might be a better way
			global pos_mean, neg_mean, pos_data_analysis, neg_data_analysis
			global temp_count, total_count, total_count_mean
			global timestamps

			pmean = mean(pos_data_analysis)
			nmean = mean(neg_data_analysis)

			pos_mean.append(pmean)
			neg_mean.append(nmean)
			total_count.append(temp_count)
			total_count_mean.append(mean(total_count))

			timestamps.append(time.strftime("%H:%M:%S", time.localtime())) #gets timestamps at the moment

			# print("Standard deviation: {}".format(np.std(total_count, ddof=1)))
			print("tempcount: {};\nposcount: {}, with sentiment: {};\nnegcount: {}, with sentiment: {}\n".format(temp_count,
															len(pos_data_analysis), pmean, len(neg_data_analysis), nmean))

			#resets
			pos_data_analysis = []
			neg_data_analysis = []
			temp_count = 0
		
		time.sleep(1) # so it wont repeat more than once on each interval


# here is will be ok to keep multiple threads, since Queue is threadsafe
def sentiment_worker(thread_name):
	print("Thread {}...".format(thread_name))
	global temp_count
	while True:
		# print(q.empty())
		if not q.empty():
			data = q.get()
			sentiment = nlp.get_sentimentVals(data)

			if sentiment > 0:
				pos_data_analysis.append(sentiment)
			elif sentiment < 0:
				neg_data_analysis.append(sentiment)

			temp_count+=1


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
	mean2list = Thread(target=mean_into_lst)
	# add a thread that checks the time adds the data to a 
	threads = [q_loader_worker, q_checker, mean2list]

	for i in range(2):
		threads.append(Thread(target=sentiment_worker, args=('Sentiment worker #{} starting...'.format(i+1),)))

	# daemon makes sure that each thread stops if and when the main thread stops
	for thread in threads:
		thread.daemon = True
		thread.start()

	ani = animation.FuncAnimation(fig, animate, interval=900)
	plt.show()


if __name__ == '__main__':
	main()