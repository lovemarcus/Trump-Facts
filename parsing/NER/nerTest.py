from nltk.tag import StanfordNERTagger
from itertools import groupby

def namedEntityRecognition( text):
    new_text = text.encode('ascii','ignore')
    st = StanfordNERTagger('english.all.3class.distsim.crf.ser.gz')
    return st.tag(text.split())

netagged_words = namedEntityRecognition( 'Rami Eid and Amanda Johsson is studying at Stony Brook University in NY and will later go to Washington' )
for tag, chunk in groupby(netagged_words, lambda x:x[1]):
    if tag == "PERSON":
        print("%-12s"%tag, " ".join(w for w, t in chunk))
    elif tag == "LOCATION":
        print("%-12s"%tag, " ".join(w for w, t in chunk))
    elif tag == "ORGANIZATION":
        print("%-12s"%tag, " ".join(w for w, t in chunk))
