import sys
import tweepy
import json
import time
import re

import streamKeys as sk # contains the api keys

# what makes RabbitMQ stick together and work
import pika

#global queue name
queue_name = 'twitter_topic_feed'

# globals needd for authentification (can be changed later)
key = sk.key
secret = sk.secret

access_token = sk.access_token
a_token_secret = sk.a_token_secret

# class that will stream the chosen data into rabbit mqq
class CustomStreamListener(tweepy.StreamListener):
	def __init__(self, api):
		self.api = api
		super(tweepy.StreamListener, self).__init__()

		#setup rabbitMQ Connection
		connection = pika.BlockingConnection(
			pika.ConnectionParameters(host='localhost')
		)
		self.channel = connection.channel()

		#set max queue size
		args = {"x-max-length": 2000}

		self.channel.queue_declare(queue=queue_name, arguments=args)


	def on_status(self, status):
		
		# this is program specific since the data anaylisis will be done after
		# and it feels redundant to queue it if it will be dumped later
		if status.lang == 'en':

			# this will be more usfull down the line leave it as of now

			data = {}
			data['text'] = status.text.replace('\n', ' ').replace('\r', ' ')
			data['created_at'] = time.mktime(status.created_at.timetuple()) # convert the json into a time tuple
			data['geo'] = status.geo
			data['source'] = status.source

			# send just the text since it's the only indicator needed
			single_line = clean_data(status.text)

			# queue the tweet (can use a dic[will be json] instead of a single line)
			self.channel.basic_publish(exchange='', routing_key=queue_name, body=single_line)


	def on_error(self, status_code):
		print('Encountered error with status code: {}'.format(status_code), file=sys.stderr)
		return True  # Don't kill the stream

	def on_timeout(self):
		print('Timeout...', file=sys.stderr)
		return True  # Don't kill the stream

# creates the authentification object given the  imported data
def _login():
	# login data
	auth = tweepy.OAuthHandler(key, secret)
	auth.set_access_token(access_token, a_token_secret)

	api = tweepy.API(auth)

	return auth,api

#cleaning the data to make the line smaller and NLP more efficient
def clean_data(line):
	# remove urls 
	new_line = re.sub(r"http\S+", "", line)

	# get rid of the RT indication of retweets. Nlp efficiency
	# not sure if it's slang for something so just removing the first one
	# therefore no regex
	if new_line[:3] == 'RT ':
		new_line = new_line[3:]

	return new_line


# THIS MIGHT NOT BE NEEDED SINCE I CAN JUST UPDATE THE QUEUE
def init_stream(key_str):
	w_auth, w_api = _login()
	listener = CustomStreamListener(w_api)     # UPDATED LATER
	stream = tweepy.Stream(w_auth, listener) # UPDATE LATER
	key_lst = list(key_str)
	stream.filter(track=key_lst)


def parse_keywords():
	preset = 'Tesla'
	try:
		# load keywords
		argz = sys.argv[1:]
		#break the 'underscore' so you can pass compund words
		keywords = list(map(lambda x: x.replace('_', ' '), argz))
		init_stream(keywords)
	except IndexError:
		init_stream(preset)


preset = 'Tesla'

def main():
	parse_keywords()

if __name__ == '__main__':
	main()
