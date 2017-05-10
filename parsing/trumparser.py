# -*- coding: utf-8 -*-
import json
import os
#from itertools import groupby

import io
import nltk
import requests
import zipfile
from elasticsearch import Elasticsearch
from geopy.geocoders import Nominatim
from nltk.tag import StanfordNERTagger
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class TrumParser:
    def __init__(self, index: str = "twitter", url: str ='http://localhost:9200'):
        self.analyzer = SentimentIntensityAnalyzer()
        #self.st = StanfordNERTagger('english.all.3class.distsim.crf.ser.gz')
        self.geolocator = Nominatim()
        self.index = index
        self.url = url
        self.months_dict = {
                            'Jan': u'01', 'Feb': u'02', 'Mar': u'03', 'Apr': u'04', 'May': u'05',
                            'Jun': u'06', 'Jul': u'07', 'Aug': u'08', 'Sep': u'09', 'Oct': u'10', 
                            'Nov': u'11', 'Dec': u'12'
                            }
        with open('mapping.txt', 'r') as myfile:
            self.mapping = myfile.read().replace('\n', '')

    def extract_relevant_fields_tweet(self, json_tweet: dict) -> dict:
        """
        Extracts relevant information out from a given tweet
        :param json_tweet: Tweet in JSON format
        :return: Dictionary containing the relevant fields extracted from the tweet
        """
        tweet = dict()

        # Tweet text
        tweet["text"] = json_tweet.get("text")

        # Get persons, locations and organizations using NLTK
        ne = process_language(tweet["text"])
        for key, value in ne.items():
            tweet[key] = value

        # Get date and hour
        tweet["date"], tweet["hour"] = self.get_date_and_hour(json_tweet)

        # Users and hashtags mentioned in the tweet (e.g. @MELANIATRUMP)
        tweet["users_mentioned"] = get_users_mentioned(json_tweet)
        tweet["hashtags_mentioned"] = get_hashtags_mentioned(json_tweet)

        # Number of times this Tweet has been retweeted and favourited
        tweet["retweet_count"] = json_tweet.get("retweet_count")
        tweet["favorite_count"] = json_tweet.get("favorite_count")

        # Get sentiment impact from the tweet
        tweet["sentiment"] = self.get_sentiment(tweet["text"])

        """"# Get persons, locations and organizations using NER by Stanford, Note: very slow segment...
        netagged_words = self.named_entity_recognition(tweet["text"])
        tweet["NER_PERSON"] = []
        tweet["NER_LOCATION"] = []
        tweet["NER_ORGANIZATION"] = []
        tweet["geo_location"] = []
        for tag, chunk in groupby(netagged_words, lambda x: x[1]):
            if tag == "PERSON":
                tweet["NER_PERSON"].append(" ".join(w for w, t in chunk))
            elif tag == "LOCATION":
                loc = " ".join(w for w, t in chunk)
                tweet["NER_LOCATION"].append(loc)
                try:
                    geo_elem = self.geolocator.geocode(loc)
                    tweet["geo_location"].append(str(geo_elem.latitude) + ',' + str(geo_elem.longitude))
                except AttributeError:
                    print("Failed Conversion: " + loc)
            elif tag == "ORGANIZATION":
                tweet["NER_ORGANIZATION"].append(" ".join(w for w, t in chunk))"""

        return tweet

    def get_date_and_hour(self, json_tweet: dict) -> tuple((str, int)):
        """
        Obtains the time and hour a certain tweet was published
        :param json_tweet: Tweet in JSON format
        :return: One string containing the date and one integer containing the hour
        """
        d = json_tweet.get("created_at").split(" ")
        date = d[5] + u"/" + self.months_dict[d[1]] + u'/' + d[2] + u' ' + d[3]
        # Tweet hour
        utc_offset = json_tweet.get("user").get("utc_offset")/3600
        h = str(d[3])
        hour = int(h[0:2]) + int(utc_offset)
        if hour < 0:
            hour += 24
        return date, hour

    def get_sentiment(self, text: str) -> float:
        """
        Get sentiment value from the given text using VADER sentiment analysis tools
        :param text: Tweet text as a string
        :return: Float containing the sentiment of the input tweet string
        """
        return self.analyzer.polarity_scores(text).get("compound")

    def named_entity_recognition(self, text: str):
        """
        Obtain persons, locations and organizations mentioned in the given tweet using Named-Entity Recognition (NER)
        tool by Stanford
        :param text: Tweet text as a string
        :return: List containing
        """
        return self.st.tag(text.split())

    def post_to_elastic(self, directory_downloaded_data, n_twitts=5e10) -> None:
        """
        posts the content in directory_original_data to ElasticSearch
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
                # t0 = time.time()

                # Test on small portion of the data
                if idx > n_twitts:
                    break

                # Load JSON file
                with open(path_to_file) as raw_tweets:
                    raw_tweets = json.load(raw_tweets)
                    # t_parsing = 0
                    # t_index = 0
                    print(len(raw_tweets), "tweets from", path_to_file)  # , end="... ")
                    for raw_tweet in raw_tweets:
                        # Extract the relevant features from each tweet in json_tweets
                        #  t1 = time.time()
                        parsed_tweet = self.extract_relevant_fields_tweet(raw_tweet)
                        #  t_parsing += time.time()-t1

                        # Post to ElasticSearch
                        # t1 = time.time()
                        es.index(index=self.index, doc_type='tweet', id=idx, body=parsed_tweet)
                        # t_index += time.time()-t1
                        #  Increment Index
                        idx += 1
                        # print("Total time: %.2f" % (time.time()-t0))
                        # print("Average Parsing time: \t %.2f ms" % (1000*t_parsing/float(len(raw_tweets))))
                        # print("Average Index time: \t %.2f ms" % (1000*t_index/float(len(raw_tweets))))

        elif res.status_code != 200:
            print("Elastic not found at", self.url)

        print("\nTweets successfully posted!")

    def create_index(self) -> None:
        """
        Creates the defined index in ElasticSearch
        """
        res = requests.get(self.url)
        es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        if res.status_code == 200:
            es.indices.create(index=self.index, ignore=400, body=self.mapping)
        elif res.status_code != 200:
            print("Elastic not found at", self.url)

    def delete_index(self) -> None:
        """
        Deletes the created index from ElasticSearch
        """
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


def maybe_download_files(directory_downloaded_data: str, force_update_2017=False) -> None:
    """
    Potentially downloads the missing files using The Trump Archive by github@bpb27
    :param directory_downloaded_data: Path to store the downloaded files
    :param force_update_2017: Set to true if an update of 2017 tweets is wanted
    """
    url = "https://github.com/bpb27/trump_tweet_data_archive/raw/master/master_"

    files = ('2009.json', '2010.json', '2011.json', '2012.json', '2013.json',
             '2014.json', '2015.json', '2016.json', '2017.json')

    break_line = False

    for file in files:
        path_to_file = os.path.join(directory_downloaded_data, "master_" + file)
        if not os.path.exists(path_to_file):
            file_url = url + file + ".zip"
            print("> Downloading", file_url, "...")
            r = requests.get(file_url)
            z = zipfile.ZipFile(io.BytesIO(r.content))
            z.extractall(path=directory_downloaded_data)
            break_line = True
            if file == files[-1]:
                force_update_2017 = False

    if force_update_2017:
        file_url = url + files[-1] + ".zip"
        print("> Retrieving last tweets in 2017 from", file_url, "...")
        r = requests.get(file_url)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(path=directory_downloaded_data)
        break_line = True

    if break_line:
        print("")
    else:
        print("Nothing to download")


def get_users_mentioned(json_tweet) -> list:
    """
    Returns users mentioned in the given tweet
    :param json_tweet:
    :return: List with all the users mentioned as strings
    """
    return [user_mentioned.get("screen_name") for user_mentioned in json_tweet.get("entities").get("user_mentions")]


def get_hashtags_mentioned(json_tweet) -> list:
    """
    Returns hashtags mentioned in the given tweet
    :param json_tweet:
    :return: List with all the hashtags as strings
    """
    return [hashtags.get("text") for hashtags in json_tweet.get("entities").get("hashtags")]


def process_language(text: str) -> dict:
    """
    Processes the input text and obtains mentioned persons, organizations and locations
    :param text: Tweet text as a string
    :return:
    """
    try:
        tagged = nltk.pos_tag(nltk.word_tokenize(text.replace("@", "")))
        ne_tagged = nltk.ne_chunk(tagged)
        words = []
        adjectives = []
        for t in tagged:
            if (t[1] == 'NN') or (t[1] == 'NNS') or (t[1] == 'NNP') or (t[1] == 'NNPS'):
                words.append(t[0])
            if (t[1] == 'JJ') or (t[1] == 'JJS') or (t[1] == 'JJP'):
                adjectives.append(t[0])
        words.append(adjectives)

        named_entities = {'words': words, 'NLTK_PERSON': [], 'NLTK_ORGANIZATION': [], 'NLTK_LOCATION': []}

        for entity in ne_tagged:
            if isinstance(entity, nltk.tree.Tree):
                etext = " ".join([word for word, tag in entity.leaves()])
                label = entity.label()
            else:
                continue

            if label == 'PERSON':
                key = 'NLTK_PERSON'
            elif label == 'ORGANIZATION':
                key = 'NLTK_ORGANIZATION'
            elif label == 'LOCATION':
                key = 'NLTK_LOCATION'
            else:
                key = None

            if key:
                named_entities[key].append(etext)

        return named_entities

    except NameError as e:
        print(str(e))
    return None
