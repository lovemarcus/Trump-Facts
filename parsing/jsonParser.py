# -*- coding: utf-8 -*-
from trumparser import TrumParser, maybe_download_files, update_location_dictionary
from optparse import OptionParser

# Create a parser to add options
parser = OptionParser()
usage = "usage: %prog [options] "
parser.add_option("-u", "--update", action="store_true", default=False,
                  help="update the geo coordinates (can take some time)",
                  dest="update_locations")
parser.add_option("-x", "--download", action="store_true", default=False,
                  help="download new tweets",
                  dest="download_new_tweets")
parser.add_option("-d", "--delete", action="store_true", default=False,
                  help="delete index",
                  dest="delete_index")
options, arguments = parser.parse_args()

# Update locations
if options.update_locations:
    update_location_dictionary('outfile.txt')

Trump = TrumParser()
if options.delete_index:
    Trump.delete_index()
Trump.create_index()
# Store download files in /data. We force the script to retrieve last tweets from this year!
if options.download_new_tweets:
    maybe_download_files(directory_downloaded_data='data', force_update_2017=False)

# Change the parameter n_twitts to post a lower amount of tweets
Trump.post_to_elastic(directory_downloaded_data='data', n_twitts=30000)
#print("Words removed:")
#for w in Trump.removedwords:
#    print(w)
print("Number of different words: \t %d" % len(Trump.words))
print("Number of different words after clustering: \t %d" % len(Trump.newwords))
""""date":{
          "type":"date",
          "format":"yyyy/MM/dd HH:mm:ss"
        }"""
