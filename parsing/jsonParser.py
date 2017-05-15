# -*- coding: utf-8 -*-
from trumparser import TrumParser, maybe_download_files, update_location_dictionary
from optparse import OptionParser

# Create a parser to add options
parser = OptionParser()
usage = "usage: %prog [options] "
parser.add_option("-u", "--update", action="store_true", default=False,
                  help="update the geo coordinates (can take some time)",
                  dest="update_locations")
options, arguments = parser.parse_args()

# Update locations
if options.update_locations:
    update_location_dictionary('outfile.txt')

Trump = TrumParser()
# Trump.delete_index()
Trump.create_index()
# Store download files in /data. We force the script to retrieve last tweets from this year!
maybe_download_files(directory_downloaded_data='data', force_update_2017=False)

# Change the parameter n_twitts to post a lower amount of tweets
Trump.post_to_elastic(directory_downloaded_data='data', n_twitts=1e5)

""""date":{
          "type":"date",
          "format":"yyyy/MM/dd HH:mm:ss"
        }"""
