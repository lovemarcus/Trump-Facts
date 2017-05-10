from zipfile import ZipFile
from urllib.request import urlopen
import os
import nltk

# 1. Download NER
if not os.path.exists('NER'):
    print("NER files already downloaded (at least there is a folder called NER!)")
else:
    print("> Downloading NER dependencies")
    zipurl = "http://nlp.stanford.edu/software/stanford-ner-2015-04-20.zip"
    zipresp = urlopen(zipurl)
    tempzip = open("/tmp/tempfile.zip", "wb")
    tempzip.write(zipresp.read())
    tempzip.close()
    zf = ZipFile("/tmp/tempfile.zip")
    zf.extractall(path = 'NER')
    # close the ZipFile instance
    zf.close()

# 2. Download NLTK stuff
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('punkt')
nltk.download('maxent_treebank_pos_')
nltk.download('averaged_perceptron_tagger')

