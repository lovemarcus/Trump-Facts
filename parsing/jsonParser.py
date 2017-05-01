from trumparser import TrumParser

Trump = TrumParser()
# Trump.delete_index()
Trump.create_index()
Trump.download_files('data')
Trump.post_to_elastic('data')
