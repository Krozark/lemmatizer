from .const import LEMMATIZER_DATA_DIRECTORY_PATH, LEMMATIZER_DICTIONARY_FILENAME_TEMPLATE
import os

class Lookup:
    def __init__(self, lang:str):
        self._lang :str = lang

    def get_lemma(self):
        raise NotImplementedError

class DictionaryLookups(Lookup):

    def __init__(self,lang:str):
        super().__init__(lang)
        self._dict = {}

    def _get_file_path(self):
        filename = LEMMATIZER_DICTIONARY_FILENAME_TEMPLATE % self._lang
        path = os.path.join(LEMMATIZER_DATA_DIRECTORY_PATH, filename)
        return path

    def _load_from_disk(self, reset=True):
        path = self._get_file_path()

        if not os.path.isfile(path):
            raise RuntimeError(f"File {path} don’t exists.")

        with open(path, "r") as f:
            try:
                data = {} if reset else self._dict
                for line in f:
                    word, lemma = line.split("\t")
                    if word in data:
                        data[word].add(lemma)
                    else:
                        data[word] = {lemma}
                self._dict = data
            except Exception as e:
                raise RuntimeError(f"File {path} is not a valid data.") from e