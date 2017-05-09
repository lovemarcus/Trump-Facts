# -*- coding: utf-8 -*-
import os
import requests, zipfile, io, time
from datetime import datetime
from elasticsearch import Elasticsearch
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
import re
import time
from nltk.tag import StanfordNERTagger
from itertools import groupby
from geopy.geocoders import Nominatim

class TrumParser():

	def __init__(self, index="twitter", url='http://localhost:9200'):
		self.analyzer = SentimentIntensityAnalyzer()
		self.st = StanfordNERTagger('english.all.3class.distsim.crf.ser.gz')
		self.geolocator = Nominatim()
		self.index = index
		self.url = url
		self.months_dict = {'Jan':u'01','Feb':u'02', 'Mar':u'03' ,'Apr':u'04', 'May':u'05',\
	'Jun':u'06','Jul':u'07', 'Aug':u'08', 'Sep':u'09', 'Oct':u'10', 'Nov':u'11', 'Dec':u'12'}
		with open('mapping.txt', 'r') as myfile:
			self.mapping = myfile.read().replace('\n', '')



	def maybe_download_files(self, directory_downloaded_data, force_update_2017=False):
		"""
		Creates a directory named 'directory' with the json files contianign Trump's tweets if it
		does not exist
		"""
		url = 'https://github.com/bpb27/trump_tweet_data_archive/raw/master/master_'

		files = ['2009.json', '2010.json', '2011.json', '2012.json', '2013.json', \
		'2014.json', '2015.json', '2016.json', '2017.json']

		break_line = False

		for file in files:
			path_to_file = os.path.join(directory_downloaded_data, "master_"+file)
			if not os.path.exists(path_to_file):
				file_url = url+file+".zip"
				print("> Downloading", file_url, "...")
				r = requests.get(file_url)
				z = zipfile.ZipFile(io.BytesIO(r.content))
				z.extractall(path=directory_downloaded_data)
				break_line = True
		if force_update_2017 == True:
			file_url = url+files[-1]+".zip"
			print("> Retrieving last tweets in 2017 from", file_url, "...")
			r = requests.get(file_url)
			z = zipfile.ZipFile(io.BytesIO(r.content))
			z.extractall(path=directory_downloaded_data)
			break_line = True

		if break_line:
			print("")
		else:
			print("Nothing to download")


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
		# Get important words
		tweet["words"] = self.processLanguage(tweet["text"])
		# Date tweet publication
		d = json_tweet.get("created_at")
		date_conv = d.split(" ")
		tweet["date"] = date_conv[5] + u"/" + self.months_dict[date_conv[1]] +u'/'\
		+ date_conv[2] +u' ' + date_conv[3]
		# Tweet source
		# tweet["source"] = json_tweet.get("source")
		# Users mentioned in the tweet (e.g. @MELANIATRUMP)
		tweet["users_mentioned"] = [user_mentioned.get("screen_name") for user_mentioned in json_tweet.get("entities").get("user_mentions")]
		tweet["hashtags"] = [hashtags.get("text") for hashtags in json_tweet.get("entities").get("hashtags")]
		# Number of times this Tweet has been retweeted
		tweet["retweet_count"] = json_tweet.get("retweet_count")
		# How many times this Tweet has been liked by Twitter users.
		tweet["favorite_count"] = json_tweet.get("favorite_count")
		# Followers at the time of the tweet
		tweet["user_followers"] = json_tweet.get("user").get("followers_count")
		# Sentiment Analysis
		tweet["sentiment"] = self.get_sentiment(tweet["text"])
		# Named-Enity Recognition, Note: very slow segment...
		netagged_words = self.namedEntityRecognition(tweet["text"])
		tweet["NER_PERSON"] = []
		tweet["NER_LOCATION"] = []
		tweet["NER_ORGANIZATION"] = []
		tweet["location"] = []
		for tag, chunk in groupby(netagged_words, lambda x:x[1]):
			if tag == "PERSON":
				tweet["NER_PERSON"].append( " ".join(w for w, t in chunk) )
			elif tag == "LOCATION":
				loc = " ".join(w for w, t in chunk)
				tweet["NER_LOCATION"].append( loc )
				try:
					location = self.geolocator.geocode( loc )
					tweet["location"].append( str(location.latitude) + ',' + str(location.longitude) )
				except AttributeError as ae:
					print("Failed Convertion: " + loc)
			elif tag == "ORGANIZATION":
				tweet["NER_ORGANIZATION"].append( " ".join(w for w, t in chunk) )
		return tweet


	# Use VADER sentiment analysis
	def get_sentiment(self, text):
		new_text = text.encode('ascii','ignore')
		#print(new_text)
		#print(analyzer.polarity_scores(new_text))
		return self.analyzer.polarity_scores(text).get("compound")

	# Use Stanford named-enity recognition (PERSON, LOCATION, ORGANIZATION)
	def namedEntityRecognition(self, text):
		new_text = text.encode('ascii','ignore')
		return self.st.tag(text.split())

	# Process language and get nouns and adjectives
	def processLanguage(self,text):
		try:
			tagged = nltk.pos_tag(nltk.word_tokenize(text.replace("@","")))
			#namedEnt = nltk.ne_chunk(tagged)
			#print(tagged)
			#namedEnt.draw()
			named_entities = []
			adjectives = []
			for t in tagged:
				if (t[1] == 'NN') or (t[1] == 'NNS') or (t[1] == 'NNP') or (t[1] == 'NNPS'):
					named_entities.append(t[0])
				if (t[1] == 'JJ') or (t[1] == 'JJS') or (t[1] == 'JJP'):
					adjectives.append(t[0])
			named_entities.append(adjectives)
			return named_entities
		except Exception:
			return None


	def post_to_elastic(self, directory_downloaded_data, n_twitts=5e10):
		"""
		posts the content in directory_original_data to elasticsearch
		"""

		res = requests.get(self.url)
		es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

		if res.status_code == 200:
			idx = 0
			for filename in os.listdir(directory_downloaded_data):
				if not filename.endswith(".json"):
					continue
				path_to_file = os.path.join(directory_downloaded_data, filename)
				print("> Posting", end=" ")
				#t0 = time.time()

				# Test on small portion of the data
				if(idx>n_twitts):
					break

				# Load JSON file
				with open(path_to_file) as raw_tweets:
					raw_tweets = json.load(raw_tweets)
					# t_parsing = 0
					# t_index = 0
					print(len(raw_tweets), "tweets from", path_to_file)#, end="... ")
					for raw_tweet in raw_tweets:
						# Extract the relevant features from each tweet in json_tweets
						# t1 = time.time()
						parsed_tweet = self.extract_relevant_fields_tweet(raw_tweet)
						# t_parsing += time.time()-t1

						# Post to ElasticSearch
						# t1 = time.time()
						res2 = es.index(index=self.index, doc_type='tweet', id=idx, body=parsed_tweet)
						# t_index += time.time()-t1
						# Increment Index
						idx += 1
					#print("Total time: %.2f" % (time.time()-t0))
					#print("Average Parsing time: \t %.2f ms" % (1000*t_parsing/float(len(raw_tweets))))
					#print("Average Index time: \t %.2f ms" % (1000*t_index/float(len(raw_tweets))))

		elif res.status_code != 200:
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
		if res.status_code == 200:
			try:
				es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
				es.indices.delete(index=self.index)
				print("Index deleted!")
			except ValueError:
				print("No index to delete at", self.url)
		elif res.status_code != 200:
			print("Elastic not found at", self.url)
