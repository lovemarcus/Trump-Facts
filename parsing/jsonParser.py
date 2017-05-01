from trumparser import TrumParser

Trump = TrumParser()
Trump.create_index()
Trump.download_files('data')
Trump.post_to_elastic('data')
