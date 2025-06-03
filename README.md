# Lemmatizer

A simple approche to get lemma of words.
Those lemma are loade from a dictionnary.

## Supported languages

| language | code |
| -------- | ---- |
| french | fr |

## Usage

```python
from lemmatizer import Lemmatizer

nlp = Lemmatizer()
for lemma in nlp.get_lemma("moulons", "fr"):
    print(lemma)
```
