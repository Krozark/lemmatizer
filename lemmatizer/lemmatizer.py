from .lookups import DictionaryLookups


class Lemmatizer:
    def __init__(self, strategy=DictionaryLookups):
        self._cache = {}
        self._strategy = strategy

    def get_lemma(self, word: str, lang: str):
        if lang not in self._cache:
            self._load_lang(lang)

        return self._cache[lang].get_lemma(word)

    def _load_lang(self, lang: str):
        self._cache[lang] = self._strategy(lang=lang)
