import os

LEMMATIZER_PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))
LEMMATIZER_DATA_DIRECTORY_PATH = os.path.join(LEMMATIZER_PROJECT_PATH, "data")
LEMMATIZER_DICTIONARY_FILENAME_TEMPLATE = "dictionary-%s-word-lemma.txt"
