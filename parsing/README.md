## Parse the data

The goal of the files within this directory is to retrieve the tweets from[@realDonaldTrump](https://twitter.com/realdonaldtrump) and post them into an ElasticSearch system. To this end, we have implemented the file `trumparser.py`, which should ease this process. 

### Install dependencies

First of all, make sure that you have all the dependencies correctly installed by running
```
pip3 install -r ../requirements.txt
```

### Create an index in Elastic

You can easily create an index by simply creating a python script and importing the library, creating an object and running the method `create_index()`. 

```python
from trumparser import TrumParser

Trump = TrumParser()
Trump.createIndex()
```

By default, it will create an index with the name *twitter* at the url http:localhost:9200. In case you want to change these parameters specify them as inputs to the constructor `TrumParser()` (see more in [trumparser.py](trumparser.py)).

### Download tweets
Use the method `download_files`.

```python
Trump.download_files('data')
```

### Post the data to the Elastic Index
```python
Trump.post_to_elastic('data')
```

To run this code, you can use the provided script `jsonParser.py`. Simply run

```
python3 jsonParser.py
```

## Format of original data

The original data retrieved from the Twitter API has the following structure

```javascript
{
	'contributors': None, 
	'truncated': False, 
	'text': 'Proud of @IvankaTrump for her leadership on these important issues. Looking forward to hearing her peak at the W20! https://t.co/e6Uajrm8zp', 
	'is_quote_status': False, 
	'in_reply_to_status_id': None, 
	'id': 856830933709750272, 
	'favorite_count': 6634, 
	'source': '<a href="http://twitter.com/download/iphone" rel="nofollow">Twitter for iPhone</a>', 
	'retweeted': False, 
	'coordinates': None, 
	'entities': {
		'symbols': [], 
		'user_mentions': [{
			'indices': [9, 21], 
			'screen_name': 'IvankaTrump',
			'id': 52544275,
			'name': 'Ivanka Trump', 
			'id_str': '52544275'
		}], 
		'hashtags': [], 
		'urls': [{
			'url': 'https://t.co/e6Uajrm8zp', 
			'indices': [117, 140], 
			'expanded_url': 'https://www.ft.com/content/4d028aae-28f2-11e7-bc4b-5528796fe35c?accessToken=zwAAAVulCgEgkc9NAoquKPIR59O8S1UoeW_jXA.MEYCIQDo7n1B6DRFfoNghad5hu27qKJp_kNnHuwgcZrwlShquQIhAOgwEKdMfkR6Q8aQW6IjBzEDTh04cx985L8ETZq8Oo8u&sharetype=gift', 
			'display_url': 'ft.com/content/4d028a\u2026'
			}]
		}, 
	'in_reply_to_screen_name': None, 
	'in_reply_to_user_id': None, 
	'retweet_count': 1302, 
	'id_str': '856830933709750272', 
	'favorited': False, 
	'user': {
		'follow_request_sent': False, 
		'has_extended_profile': False, 
		'profile_use_background_image': True, 
		'time_zone': 'Eastern Time (US & Canada)', 
		'id': 25073877, 
		'default_profile': False, 
		'verified': True, 
		'profile_text_color': '333333', 
		'profile_image_url_https': 'https://pbs.twimg.com/profile_images/1980294624/DJT_Headshot_V2_normal.jpg', 
		'profile_sidebar_fill_color': 'C5CEC0', 
		'is_translator': False, 
		'geo_enabled': True, 
		'entities': {
			'description': {
				'urls': []
			}
		}, 
		'followers_count': 28313806, 
		'protected': False, 
		'id_str': '25073877', 
		'default_profile_image': False, 
		'listed_count': 68618, 
		'lang': 'en', 
		'utc_offset': -14400, 
		'statuses_count': 34791, 
		'description': '45th President of the United States of America',
		'friends_count': 45, 
		'profile_link_color': '0D5B73', 
		'profile_image_url': 'http://pbs.twimg.com/profile_images/1980294624/DJT_Headshot_V2_normal.jpg', 
		'notifications': True, 
		'profile_background_image_url_https': 'https://pbs.twimg.com/profile_background_images/530021613/trump_scotland__43_of_70_cc.jpg', 
		'profile_background_color': '6D5C18', 
		'profile_banner_url': 'https://pbs.twimg.com/profile_banners/25073877/1489657715', 
		'profile_background_image_url': 'http://pbs.twimg.com/profile_background_images/530021613/trump_scotland__43_of_70_cc.jpg', 
		'name': 'Donald J. Trump', 
		'is_translation_enabled': True, 
		'profile_background_tile': True, 
		'favourites_count': 48, 
		'screen_name': 'realDonaldTrump', 
		'url': None, 
		'created_at': 'Wed Mar 18 13:46:38 +0000 2009', 
		'contributors_enabled': False, 
		'location': 'Washington, DC', 
		'profile_sidebar_border_color': 'BDDCAD', 
		'translator_type': 'regular', 'following': True
	}, 
	'geo': None, 
	'in_reply_to_user_id_str': None, 
	'possibly_sensitive': False, 
	'lang': 'en', 
	'created_at': 'Tue Apr 25 11:23:08 +0000 2017', 
	'in_reply_to_status_id_str': None, 'place': None
}
```