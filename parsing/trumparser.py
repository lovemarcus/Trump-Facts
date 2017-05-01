# -*- coding: utf-8 -*-
import os
import requests, zipfile, io
from datetime import datetime
from elasticsearch import Elasticsearch
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class TrumParser():

	def __init__(self, index="twitter", url='http://localhost:9200'):
		self.index = index
		self.url = url
		self.months_dict = {'Jan':u'01','Feb':u'02', 'Mar':u'03' ,'Apr':u'04', 'May':u'05',\
	'Jun':u'06','Jul':u'07', 'Aug':u'08', 'Sep':u'09', 'Oct':u'10', 'Nov':u'11', 'Dec':u'12'}
		self.mapping = '''{  
						  "mappings":{ 
						    "trump":{  
						      "properties":{  
						        "date":{  
						          "type":"date",
						          "format":"yyyy/MM/dd HH:mm:ss"
						        },
						        "text":{
						          "type": "text"
						        },
						        "users_mentioned":{
						          "type": "keyword"
						        },
						        "hashtags":{
						          "type": "keyword"
						        },
						        "retweet_count":{
						          "type": "integer"
						        },
						        "favorite_count":{
						          "type": "integer"
						        },
						        "user_followers":{
						          "type": "integer"
						        },
						        "sentiment":{
						          "type":"double"
						        }
						      }
						    }
						  }
						}'''


	def download_files(self, directory):
		"""
		Creates a directory named 'directory' with the json files contianign Trump's tweets if it
		does not exist
		"""
		url = 'https://github.com/bpb27/trump_tweet_data_archive/raw/master/master_'

		files = ['2009.json', '2010.json', '2011.json', '2012.json', '2013.json', \
		'2014.json', '2015.json', '2016.json', '2017.json']

		break_line = False

		print("Downloading data")
		for file in files:
			path_to_file = os.path.join(directory, "master_"+file)
			if not os.path.exists(path_to_file):
				file_url = url+file+".zip"
				print("> Downloading", file_url, "...")
				r = requests.get(file_url)
				z = zipfile.ZipFile(io.BytesIO(r.content))
				z.extractall(path=directory)
				break_line = True
		if break_line: 
			print("")


	def extract_relevant_fields_tweet(self, json_tweet):
		"""
		Creates a dictionary using only the relevant fields from json_tweet
		json_tweet : dictionary containing all the fields from Twitter API 
		"""
		# Increase retweet counter
		"""if tweet.get("retweeted"):
			retweet_nb +=1"""
		tweet = {}
		# Get user information #
		#tweet["user_description"] = json_tweet.get("user").get("description")
		#tweet["location"] = json_tweet.get("user").get("location")

		# Tweet text
		tweet["text"] = json_tweet.get("text")
		# Date tweet publication
		d = json_tweet.get("created_at")
		date_conv = d.split(" ")
		tweet["date"] = date_conv[5] + u"/" + self.months_dict[date_conv[1]] +u'/'\
		+ date_conv[2] +u' ' + date_conv[3]
		# Tweet source
		# tweet["source"] = json_tweet.get("source")
		# Users mentioned in the tweet (e.g. @MELANIATRUMP)
		tweet["users_mentioned"] = [user_mentioned.get("screen_name") for user_mentioned in json_tweet.get("entities").get("user_mentions")]
		tweet["hashtags"] = [user_mentioned.get("text") for hashtags in json_tweet.get("entities").get("hashtags")]
		# Number of times this Tweet has been retweeted
		tweet["retweet_count"] = json_tweet.get("retweet_count")
		# How many times this Tweet has been liked by Twitter users.
		tweet["favorite_count"] = json_tweet.get("favorite_count")
		# Followers at the time of the tweet
		tweet["user_followers"] = json_tweet.get("user").get("followers_count")
		# Sentiment Analisis
		tweet["sentiment"] = get_sentiment(analyzer, tweet["text"])
		
		return tweet


	# Use VADER sentiment analysis
	def get_sentiment(self, analyzer, text):
		new_text = text.encode('ascii','ignore')
		#print(new_text)
		#print(analyzer.polarity_scores(new_text))
		return float(analyzer.polarity_scores(new_text).get("compound"))
	

	def post_to_elastic(self, directory_original_data):
		"""
		posts the content in directory_original_data to elasticsearch
		"""
		res = requests.get(self.url)
		es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

		while res.status_code == 200:			
			idx = 0
			for filename in os.listdir(directory_original_data):
				if not filename.endswith(".json"):
					continue
				path_to_file = os.path.join(directory_original_data, filename)
				print("> Posting tweets in", path_to_file)

				# Load JSON file
				with open(path_to_file) as raw_tweets:
					raw_tweets = json.load(raw_tweets)
					
					for raw_tweet in raw_tweets:
						# Extract the relevant features from each tweet in json_tweets
						parsed_tweet = self.extract_relevant_fields_tweet(raw_tweet)
						# Post to ElasticSearch
						res2 = es.index(index=self., doc_type='tweet', id=idx, body=parsed_tweet)
						# Increment Index
						idx += 1

		if res.status_code != 200:
			print("Elastic not found at", self.url)

		print("\nTweets succesfully posted!")


	def create_index(self):
		res = requests.get(self.url)
		es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
		if res.status_code == 200:
			es.indices.create(index=self.index, ignore=400, body=self.mapping)
		elif res.status_code != 200:
			print("Elastic not found at", self.url)


	def delete_index(self):
		res = requests.get(self.url)
		es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
		if res.status_code == 200:
			es.indices.delete(index=self.index)
		elif res.status_code != 200:
			print("Elastic not found at", self.url)
