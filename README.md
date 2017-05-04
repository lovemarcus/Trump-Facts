# Trump-Facts


---
>	:calendar:
	Next Meetingss: (1) Wednesday 10th May, 9:00 AM at the [KTH Bib](https://www.google.se/maps/place/KTH+Biblioteket/@59.34789,18.072871,15z/data=!4m2!3m1!1s0x0:0x80f2dd1472d9a0fa?sa=X&ved=0ahUKEwiIs-nCv83TAhWkHpoKHderCygQ_BIIdjAN)
	(2) Friday 12th May, 9:00 AM at the [KTH Bib](https://www.google.se/maps/place/KTH+Biblioteket/@59.34789,18.072871,15z/data=!4m2!3m1!1s0x0:0x80f2dd1472d9a0fa?sa=X&ved=0ahUKEwiIs-nCv83TAhWkHpoKHderCygQ_BIIdjAN)

#### Current State of the project

- [X] Tweets parsed and posted to **ElasticSearch**
- [X] Sentiment Analysis of tweets
- 
- [ ] Visualization of the tweets using **Kibana**
	- [ ] Sentiment Analysis
		* Filter tweets in two categories: Positive (>0.5) and Negative (<-0.5) and obtain the two corresponding wordclouds.
		* Graphical representation of the percentile of positive tweets associated to one word.
	- [ ] Locations/People Heatmap/Wordcloud
		* Use [NER](https://nlp.stanford.edu/software/CRF-NER.shtml) or a similar tool to extract places/organizations/people mentioned by Trump's tweets
		* 
	- [ ] Hourly Tweet Histogram
- [ ] **Report** using Overleaf

---

User-friendly interface to visualize Trump Tweets using Kibana and ElasticSearch.

This project is currently being developed as part of the [DD2476 Search Engines and Information Retrieval Systems course](https://www.kth.se/student/kurser/kurs/DD2476?l=en) at [KTH Royal Institute of Technology](http://kth.se), spring 2017.

| Author              		 | GitHub                                            |
|:---------------------------|:--------------------------------------------------|
| Erik Jonas Henrik Lybecker | [elybecker](https://github.com/elybecker) 		 |
| Love Marcus 				 | [lovemarcus8](https://github.com/lovemarcus8)     |
| Robin Maillot   			 | [robin-maillot](https://github.com/robin-maillot) |
| Lucas Rodés Guirao  		 | [lucasrodes](https://github.com/lucasrodes)       |


## Data

The tweets from Trump were downloaded from [this repo](https://github.com/bpb27/trump_tweet_data_archive) by [bpb27](https://github.com/bpb27/trump_tweet_data_archive).

### Data format

The tweet data is stored in JSON files, which have been formed accessing the Twitter API. Detailed information of the fields within the JSON files can be found [here](https://dev.twitter.com/overview/api/tweets).

### Data Parsing

Not all the data provided by the Twitter API is relevant to us. Furthermore, we might want to extend it and add new fields. Thus, we provide a script to process the original data. For more detailed information look into [parsing](parsing) folder 


## Resources

- [ElasticSearch/Kibana Installation](https://github.com/lucasrodes/ES-gettingstarted/blob/master/INSTALLATION.md): Works for MacOS

- [First Steps in ElasticSearch/Kibana](https://github.com/lucasrodes/ES-gettingstarted/blob/master/firststeps.md): Some basic steps to start with ElasticSearch/Kibana
