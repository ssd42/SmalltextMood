# TweetMood
## (Work in progress)
### Small Python3 program that streams tweets directly from twitter (based on provided keywords), uses sentiment analysis to see how positive/negative they are.

### And finally loads them live into a graph in order to keep track of what people are saying about a company/person



**Needed Libraries:**

* tweepy
* json
* pika
* nltk (with the vader algorithm)
* numpy
* matplotlib
* pandas (possibly down the line)



You will need to get your own twitter keys in order to stream the tweets

## You will need to install a message queueing server (I used rabbitmq)
[Download erlang - neeeded for RabbitMQ](http://www.erlang.org/downloads)
[RabbitMQ download page](https://www.rabbitmq.com/download.html)

As of now run streamtweets to load the data into the message queueing
and run main.py to load them out of it and print out the sentiment (Threading is giving graphing an issue so its put o hold for now)

This is to insure optimal speeds in large streams and the ability to possibly use multiprocessing later down the line
