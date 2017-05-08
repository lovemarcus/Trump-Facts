# -*- coding: utf-8 -*-
from trumparser import TrumParser

Trump = TrumParser()
Trump.delete_index()
Trump.create_index()
# Store download files in /data. We force the script to retrieve last tweets from this year!
Trump.maybe_download_files(directory_downloaded_data='data', force_update_2017=True)
# Change the parameter n_twitts to post a lower amount of tweets
Trump.post_to_elastic(directory_downloaded_data='data', n_twitts=1e5)
