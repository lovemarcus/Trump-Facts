# -*- coding: utf-8 -*-
import json
import os
import io
import nltk
import requests
import zipfile
import ast
import time
from elasticsearch import Elasticsearch
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from itertools import groupby
from datetime import datetime, timedelta
import pytz

class TrumParser:
    def __init__(self, index="twitter", url='http://localhost:9200'):
        self.analyzer = SentimentIntensityAnalyzer()
        self.NER_dict = init_ner()
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
        with open('locDict.txt', 'r') as myfile:
            self.locDict = json.load(myfile)

    def extract_relevant_fields_tweet(self, json_tweet, idx):
        """
        Extracts relevant information out from a given tweet
        :param json_tweet: Tweet in JSON format
        :param idx: Tweet ID
        :return: Dictionary containing the relevant fields extracted from the tweet
        """
        tweet = dict()

        # Tweet text
        tweet["text"] = json_tweet.get("text")

        # Get persons, locations and organizations using NLTK
        ne = process_language(tweet["text"])
        for key, value in ne.items():
            tweet[key] = value
        # Get persons, locations and organizations using NER by Stanford, Note: very slow segment...
        tweet["NER_PERSON"], tweet["NER_LOCATION"], tweet["NER_ORGANIZATION"], tweet["geo_location"] = \
            self.get_persons_locations_organizations_geolocations(idx)

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

        return tweet

    def get_persons_locations_organizations_geolocations(self, idx):
        """
        Gets persons, locations (+geo_locations) and organization mentioned in the tweet
        :param idx: ID for a tweet
        :return: Four arrays containing persons, locations and organizations names + geolocation of the mentioned location
        """
        netagged_words = self.NER_dict[idx]
        person = []
        location = []
        organization = []
        geo_location = []
        for tag, chunk in groupby(netagged_words, lambda x: x[1]):
            if tag == "PERSON":
                person.append(" ".join(w for w, t in chunk))
            elif tag == "LOCATION":
                loc = " ".join(w for w, t in chunk)
                location.append(loc)
                try:
                    geo_location = self.locDict[loc]
                except KeyError as ke:
                    print("Missing Coordinates for: " + str(ke))
            elif tag == "ORGANIZATION":
                organization.append(" ".join(w for w, t in chunk))
        return person, location, organization, geo_location

    def get_date_and_hour(self, json_tweet):
        """
        Obtains the time and hour a certain tweet was published
        :param json_tweet: Tweet in JSON format
        :return: One string containing the date and one integer containing the hour
        """
        d_string = json_tweet.get("created_at")
        d = datetime.strptime(d_string, '%a %b %d %H:%M:%S +0000 %Y').replace(tzinfo=pytz.UTC)
        utc_offset = json_tweet.get("user").get("utc_offset") / 3600
        date = d + timedelta(hours=utc_offset-1)
        hour = (date.hour)# + 1) % 24
        return date, hour

    def get_sentiment(self, text):
        """
        Get sentiment value from the given text using VADER sentiment analysis tools
        :param text: Tweet text as a string
        :return: Float containing the sentiment of the input tweet string
        """
        return self.analyzer.polarity_scores(text).get("compound")

    def post_to_elastic(self, directory_downloaded_data, n_twitts=5e10):
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
                # t0 = time.time()

                # Test on small portion of the data
                if idx > n_twitts:
                    break

                # Load JSON file
                with open(path_to_file) as raw_tweets:
                    raw_tweets = json.load(raw_tweets)
                    # t_parsing = 0
                    # t_index = 0
                    print("> Posting", len(raw_tweets), "tweets from", path_to_file)  # , end="... ")
                    for raw_tweet in raw_tweets:
                        # Extract the relevant features from each tweet in json_tweets
                        #  t1 = time.time()
                        parsed_tweet = self.extract_relevant_fields_tweet(raw_tweet, idx)
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

    def create_index(self):
        """
        Creates the defined index in ElasticSearch
        """
        res = requests.get(self.url)
        es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        if res.status_code == 200:
            es.indices.create(index=self.index, ignore=400, body=self.mapping)
        elif res.status_code != 200:
            print("Elastic not found at", self.url)

    def delete_index(self):
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


def init_ner():
    """
    Loads the dictionary containing name organizations to geo_location conversion
    :return: Dictionary organization to geo_locatin conversion
    """
    fname = 'outfile.txt'
    idx = 0
    ner_lists = {}
    with open(fname, 'r') as f:
        for line in f:
            ner_lists[idx] = parse_to_list(line)
            idx += 1
    return ner_lists


def parse_to_list(s):
    """
    Converts a string(format: a, b, c) into a list (format [a, b, c])
    :param s: String (format: a, b, c)
    :return: List of values contained in string s
    """
    tuples = s.split('), ')
    out = []
    for x in tuples:
        a, b = x.split(', ')
        a = a.strip("'").strip("(''").strip("[('")
        b = b.strip("'").strip("')]\n")
        out.append((str(a), str(b)))
    return out


def maybe_download_files(directory_downloaded_data, force_update_2017=False):
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


def get_users_mentioned(json_tweet):
    """
    Returns users mentioned in the given tweet
    :param json_tweet:
    :return: List with all the users mentioned as strings
    """
    return [user_mentioned.get("screen_name") for user_mentioned in json_tweet.get("entities").get("user_mentions")]


def get_hashtags_mentioned(json_tweet):
    """
    Returns hashtags mentioned in the given tweet
    :param json_tweet:
    :return: List with all the hashtags as strings
    """
    return [hashtags.get("text") for hashtags in json_tweet.get("entities").get("hashtags")]


def process_language(text):
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


def update_location_dictionary(file_path):
    """
    Used to update locations in the dictionary and generate a corresponding file named "locDict.txt"
    :param file_path: Path containing the NER obtained names
    """
    print("> Updating locations mentioned and geo coordinates ...")
    locations = parse_locations(file_path)
    with open('locDict.txt', 'w') as outfile:
        json.dump(locations, outfile)
    f = get_fail_percentage('locDict.txt')
    print("> Finished updating %d locations, %.2f success rate" % (len(locations), f))


#
def parse_locations(file_path):
    """
    Parses locations from file and get corresponding gps coordinates if available
    :param file_path: Path containing the NER obtained names
    :return:
    """
    new_location_nb = 0
    tweets = 0
    with open('locDict.txt', 'r') as myfile:
        try:
            locations = json.load(myfile)
        except:
            locations = {}
    with open(file_path, 'r') as myfile:
        data = myfile.readlines()
        for tweet in data:
            tweets += 1
            if tweets % 1000 == 0:
                print("%d tweets processed" % tweets)
            if new_location_nb > 100:
                new_location_nb = 0
                print("saving 100 loc")
                with open('locDict.txt', 'w') as outfile:
                    json.dump(locations, outfile)

            for tag, chunk in groupby(ast.literal_eval(tweet), lambda x: x[1]):
                if tag == "LOCATION":
                    word = " ".join(w for w, t in chunk)
                    if locations.get(word) is None:
                        locations[word] = get_gps_coordinates(word, locations)
                        new_location_nb += 1
    return locations


def get_gps_coordinates(loc, locations):
    """
    Get corresponding gps coordinates to string loc
    :param loc: Location name we wish to extract the geo coordinates from
    :param locations:
    :return:
    """
    time.sleep(0.5)
    try:
        geo_elem = geocode(loc, locations)
        return str(geo_elem.latitude) + ',' + str(geo_elem.longitude)
    except AttributeError:
        # print("Failed Conversion: " + loc)
        return []


def geocode(city, locations, recursion=0):
    """
    Obtaines the geo coordinates of a location
    :param city:
    :param locations:
    :param recursion:
    :return:
    """
    print(city)
    try:
        return Nominatim().geocode(city)
    except GeocoderTimedOut as e:
        if recursion > 2:  # max recursions
            with open('locDict.txt', 'w') as outfile:
                json.dump(locations, outfile)
            f = get_fail_percentage('locDict.txt')
            print("> Timed out updating %d locations, %.2f success rate" % (len(locations), f))
            raise e
        time.sleep(2)  # wait a bit
        # try again
        return geocode(city, locations, recursion=recursion + 1)


def get_fail_percentage(file_path):
    """
    TODO
    :param file_path:
    :return:
    """
    fails = 0
    with open(file_path) as outfile:
        locations = json.load(outfile)
    for key, value in locations.items():
        if value:
            fails += 1
    return 1 - float(fails) / len(locations)
