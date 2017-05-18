import json
import pandas as pd
import matplotlib.pyplot as plt



# following function trys to load a text file
# containing json code into a list of python strings
# this is due to the Sentiment Anaylzer not working
# with certain unicode strings that give python a harder time
def text_to_jsonObj(file_name):
	return_list = []
	with open(file_name, 'r') as json_file:
		for line in json_file:
			try:
				json_line = json.loads(line)
				return_list.append(json_line)
			except:
				continue
	return return_list

def map_by(key, a_list):
	return list(map(lambda line: line[key], a_list))


def check_if_encode(encoding, line):
	try:
		a = line.encode(encoding, 'ignore')
		return True
	except:
		return False


# filters out tweets by language
def filter_by_lang(lang, alist):
	return list(filter(lambda item: 'lang' in item and item['lang']==lang, alist))

# grabs the text from the tweets
def encode_n_getText(ncoding, d_list):
	return [item['text'].encode(ncoding, 'ignore') for item in d_list]


def data_as_lst(d_list):
	# datax = [line['text'] for line in d_list]
	[print(line['text'].encode('ascii', 'ignore')) for line in d_list]
	# now make sure it has the right encoding
	return [line.encode('ascii', 'ignore') if check_if_encode('utf-8') else " " for line in datax]



# this is cool and all but its going by the pd dataframe, which may not be needed yet if at all here

# parse through the json list and extract what you want
def build_graph(data_list):
	data = pd.DataFrame()
	data['text'] = list(map(lambda tweet: tweet['text'], data_list)) #map_by('text', data_list)    
	
	# data['text'] = list(map(lambda tweet: tweet['text'], tweets_data))
	# data['lang'] = list(map(lambda tweet: tweet['lang'], tweets_data))
	# data['country'] = list(map(lambda tweet: tweet['place']['country'] if tweet['place'] != None else None, tweets_data))



	[print(line.encode('ascii', 'ignore')) if check_if_encode('utf-8', line) else "" for line in data['text']]
	print('got here')
