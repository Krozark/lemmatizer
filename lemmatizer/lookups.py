import os

from .const import LEMMATIZER_DATA_DIRECTORY_PATH, LEMMATIZER_DICTIONARY_FILENAME_TEMPLATE


class Lookup:
    def __init__(self, lang: str):
        self._lang: str = lang

    def get_lemma(self, word: str) -> list[str]:
        raise NotImplementedError


class DictionaryLookups(Lookup):
    def __init__(self, lang: str):
        super().__init__(lang)
        self._dict = {}
        self._load_from_disk()

    def get_lemma(self, word: str) -> list[str]:
        lemmas_set = self._dict.get(word.lower(), {word.lower()})
        return list(lemmas_set)

    def _get_file_path(self):
        filename = LEMMATIZER_DICTIONARY_FILENAME_TEMPLATE % self._lang
        path = os.path.join(LEMMATIZER_DATA_DIRECTORY_PATH, filename)
        return path

    def _load_from_disk(self, reset=True):
        path = self._get_file_path()

        if not os.path.isfile(path):
            raise RuntimeError(f"File {path} don’t exists.")

        with open(path) as word_lemma_file:
            try:
                data = {} if reset else self._dict
                for line in word_lemma_file.readlines():
                    line = line.rstrip()

                    if not line:
                        continue

                    word, lemma = line.split("\t")
                    if word in data:
                        data[word].add(lemma)
                    else:
                        data[word] = {lemma}
                self._dict = data
            except Exception as e:
                raise RuntimeError(f"File {path} is not a valid data.") from e
