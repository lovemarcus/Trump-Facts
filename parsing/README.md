## Parse the data

Run `jsonParser.py` and wait for it to retrieve the tweets from [@realDonaldTrump](https://twitter.com/realdonaldtrump) and place them in the root folder [`data/original_data`](../data/original_data). In case you already had downloaded them, it will skip this step. Next, it will parse the tweets to a JSON file, which will be placed in the root directory [`data/parsed_data/`](../data/parsed_data). 

```
python3 jsonParser.py
```

In case you are missing required python libraries you can install them by simply running

```
pip3 install -r ../requirements.txt
```


## Format of original data

The original data retrieved from the Twitter API has the following structure

```
{u'contributors': None, 
u'truncated': False, 
u'text': u'Proud of @IvankaTrump for her leadership on these important issues. Looking forward to hearing her speak at the W20! https://t.co/e6Uajrm8zp', 
u'is_quote_status': False, 
u'in_reply_to_status_id': None, 
u'id': 856830933709750272, 
u'favorite_count': 6634, 
u'source': u'<a href="http://twitter.com/download/iphone" rel="nofollow">Twitter for iPhone</a>', 
u'retweeted': False, 
u'coordinates': None, 
u'entities': {u'symbols': [], u'user_mentions': [{u'indices': [9, 21], u'screen_name': u'IvankaTrump', u'id': 52544275, u'name': u'Ivanka Trump', u'id_str': u'52544275'}], u'hashtags': [], 
u'urls': [{u'url': u'https://t.co/e6Uajrm8zp', u'indices': [117, 140], u'expanded_url': u'https://www.ft.com/content/4d028aae-28f2-11e7-bc4b-5528796fe35c?accessToken=zwAAAVulCgEgkc9NAoquKPIR59O8S1UoeW_jXA.MEYCIQDo7n1B6DRFfoNghad5hu27qKJp_kNnHuwgcZrwlShquQIhAOgwEKdMfkR6Q8aQW6IjBzEDTh04cx985L8ETZq8Oo8u&sharetype=gift', u'display_url': u'ft.com/content/4d028a\u2026'}]}, 
u'in_reply_to_screen_name': None, 
u'in_reply_to_user_id': None, 
u'retweet_count': 1302, 
u'id_str': u'856830933709750272', 
u'favorited': False, 
u'user': {u'follow_request_sent': False, 
	u'has_extended_profile': False, 
	u'profile_use_background_image': True, 
	u'time_zone': u'Eastern Time (US & Canada)', 
	u'id': 25073877, 
	u'default_profile': False, 
	u'verified': True, 
	u'profile_text_color': u'333333', 
	u'profile_image_url_https': u'https://pbs.twimg.com/profile_images/1980294624/DJT_Headshot_V2_normal.jpg', 
	u'profile_sidebar_fill_color': u'C5CEC0', 
	u'is_translator': False, 
	u'geo_enabled': True, 
	u'entities': {u'description': {u'urls': []}}, 
	u'followers_count': 28313806, 
	u'protected': False, 
	u'id_str': u'25073877', 
	u'default_profile_image': False, 
	u'listed_count': 68618, 
	u'lang': u'en', 
	u'utc_offset': -14400, 
	u'statuses_count': 34791, 
	u'description': u'45th President of the United States of America',
	u'friends_count': 45, 
	u'profile_link_color': u'0D5B73', 
	u'profile_image_url': u'http://pbs.twimg.com/profile_images/1980294624/DJT_Headshot_V2_normal.jpg', 
	u'notifications': True, 
	u'profile_background_image_url_https': u'https://pbs.twimg.com/profile_background_images/530021613/trump_scotland__43_of_70_cc.jpg', 
	u'profile_background_color': u'6D5C18', 
	u'profile_banner_url': u'https://pbs.twimg.com/profile_banners/25073877/1489657715', 
	u'profile_background_image_url': u'http://pbs.twimg.com/profile_background_images/530021613/trump_scotland__43_of_70_cc.jpg', 
	u'name': u'Donald J. Trump', 
	u'is_translation_enabled': True, 
	u'profile_background_tile': True, 
	u'favourites_count': 48, 
	u'screen_name': u'realDonaldTrump', 
	u'url': None, 
	u'created_at': u'Wed Mar 18 13:46:38 +0000 2009', 
	u'contributors_enabled': False, 
	u'location': u'Washington, DC', 
	u'profile_sidebar_border_color': u'BDDCAD', 
	u'translator_type': u'regular', u'following': True}, 
	u'geo': None, 
	u'in_reply_to_user_id_str': None, 
	u'possibly_sensitive': False, 
	u'lang': u'en', 
	u'created_at': u'Tue Apr 25 11:23:08 +0000 2017', 
	u'in_reply_to_status_id_str': None, u'place': None}
}
```