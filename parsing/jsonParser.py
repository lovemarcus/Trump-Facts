import json
import os

data_directory = "../Data"
tweet_nb = 0
retweet_nb = 0
new_data = []

for filename in os.listdir(data_directory):
    if filename.endswith(".json"): 
        print("reading "+ os.path.join(data_directory, filename))
	with open(os.path.join(data_directory, filename)) as json_data:
		d = json.load(json_data)
		for tweet in d:
			new_tweet = {}
			
			if tweet.get("retweeted"):
				retweet_nb +=1

			# User info
			user_description = tweet.get("user").get("description")
			user_followers = tweet.get("user").get("followers_count")
			# Tweet info
			text = tweet.get("text")
			location = tweet.get("user").get("location")
			date = tweet.get("created_at")
			source = tweet.get("source")
			mentions = []
			for user_mentionned in tweet.get("entities").get("user_mentions"):
				mentions.append(user_mentionned.get("screen_name"))
			retweets = tweet.get("retweet_count")
			favorites = tweet.get("favorite_count")
			retweeted = tweet.get("retweeted")

			new_tweet["user_description"] = user_description
			new_tweet["user_followers"] = user_followers
			new_tweet["text"] = text
			new_tweet["location"] = location
			new_tweet["date"] = date
			new_tweet["source"] = source
			new_tweet["mentions"] = mentions
			new_tweet["retweets"] = retweets
			new_tweet["favorites"] = favorites
			new_tweet["retweeted"] = retweeted
			new_data.append(new_tweet)
		#print(user_description)
		#print(user_followers)

		#print(text)
		#print(location)
		#print(date)
		#print(source)
		#print(mentions)
		#print(retweets)
		#print(favorites)
		#print(retweeted)

		#print(len(d))
		#print("\n")
		tweet_nb+=len(d)

with open('../Data/new_data.json', 'w') as outfile:
    json.dump(new_data, outfile,indent=4)

print("Tweets: "+str(tweet_nb))
print("Retweets: "+str(retweet_nb))

