import json
import os
import requests, zipfile, io
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def download_files(directory):
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

def extract_relevant_fields_tweet(json_tweet,analyzer):
	"""
	Creates a dictionary using only the relevant fields from json_tweet
	json_tweet : dictionary containing all the fields from Twitter API 
	"""
	# Increase retweet counter
	"""if tweet.get("retweeted"):
		retweet_nb +=1"""
	tweet = {}
	# Get user information #
	tweet["user_description"] = json_tweet.get("user").get("description")
	tweet["user_followers"] = json_tweet.get("user").get("followers_count")
	tweet["location"] = json_tweet.get("user").get("location")

	# Tweet text
	tweet["text"] = json_tweet.get("text")
	# Date tweet publication
	tweet["date"] = json_tweet.get("created_at")
	date_conv = tweet["date"].split(" ")
	tweet["_timestamp"] = date_conv[5] + u"-" + months_dict[date_conv[1]] +u'-'+ date_conv[2] +u'T' + date_conv[3]
	# Tweet source
	tweet["source"] = json_tweet.get("source")
	# Users mentioned in the tweet (e.g. @MELANIATRUMP)
	tweet["users_mentioned"] = [user_mentioned.get("screen_name") for user_mentioned in json_tweet.get("entities").get("user_mentions")]
	# Number of times this Tweet has been retweeted
	tweet["retweet_count"] = json_tweet.get("retweet_count")
	# How many times this Tweet has been liked by Twitter users.
	tweet["favorite_count"] = json_tweet.get("favorite_count")
	tweet["sentiment"] = get_sentiment(analyzer,tweet["text"])
	
	return tweet

# Use VADER sentiment analysis
def get_sentiment(analyzer,text):
	new_text = text.encode('ascii','ignore')
	#print(new_text)
	#print(analyzer.polarity_scores(new_text))
	return float(analyzer.polarity_scores(new_text).get("compound"))

if __name__ == "__main__":

	count_tweets = 0 # Counter of the tweets
	count_retweets = 0 # Counter of the retweets
	# Directory names
	directory_data = "../data"
	directory_original_data = directory_data+"/original_data"
	directory_parsed_data = directory_data+"/parsed_data"

	analyzer = SentimentIntensityAnalyzer()

	# Create directories if they does not exist
	if not os.path.exists(directory_data):
		print("Creating directory", directory_data)
		os.makedirs(directory_data)
	if not os.path.exists(directory_original_data):
		print("Creating directory", directory_original_data)
		os.makedirs(directory_original_data)
	if not os.path.exists(directory_parsed_data):
		print("Creating directory", directory_parsed_data)
		os.makedirs(directory_parsed_data)
	print("")

	final_data = {'tweets':[]}
	download_files(directory_original_data) # Downloads and extracts files if not found in directory_original_data

	months_dict = {'Jan':u'01','Feb':u'02', 'Mar':u'03' ,'Apr':u'04', 'May':u'05',\
	'Jun':u'06','Jul':u'07', 'Aug':u'08', 'Sep':u'09', 'Oct':u'10', 'Nov':u'11', 'Dec':u'12'}

	print("Reading JSON data")
	# Look for JSON files within the specified directory
	for filename in os.listdir(directory_original_data):
		if not filename.endswith(".json"):
			continue
		path_to_file = os.path.join(directory_original_data, filename)
		print("> Reading", path_to_file)

		# Load JSON file
		with open(path_to_file) as raw_tweets:
			raw_tweets = json.load(raw_tweets)
			# Number of tweets contained in json_tweets
			count_tweets+=len(raw_tweets)

			# Extract the relevant features from each tweet in json_tweets
			for raw_tweet in raw_tweets:
				parsed_tweet = extract_relevant_fields_tweet(raw_tweet,analyzer)
				final_data['tweets'].append(parsed_tweet)
				count_retweets += parsed_tweet['retweet_count']

	print("")
	print("Storing the data...")

	# Store parsed data
	with open(directory_parsed_data+'/new_data.json', 'w') as outfile:
	    json.dump(final_data, outfile,indent=4)
	    print("> Data succesfully stored!")

	print("")
	print("Brief summary")
	print("> Number of tweets: "+str(count_tweets))
	print("> Number of retweets: "+str(count_retweets))
