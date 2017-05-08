from itertools import groupby
for tag, chunk in groupby(netagged_words, lambda x:x[1]):
    if tag != "O":
        print("%-12s"%tag, " ".join(w for w, t in chunk))
