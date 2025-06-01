import lzma
import os
import pickle
import sys
from collections import defaultdict
from operator import itemgetter

import spacy
from tqdm import tqdm


def extract_plzma(file_path: str):
    column_pairs = []
    with lzma.open(file_path, "rb") as filehandle:
        pickled_dict = pickle.load(filehandle)
        assert isinstance(pickled_dict, dict)
        for text, lemma in tqdm(pickled_dict.items(), desc=f"Loading {file_path}"):
            column_pairs.append((text.decode().strip(), lemma.decode().strip()))

    return column_pairs

def extract_mlex(file_path):
    column_pairs = []

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in tqdm(file, desc=f"Loading {file_path}"):
            columns = line.strip().split('\t')
            l = len(columns)
            to_add = []
            if l >=5:
                to_add.append((columns[0], columns[4]))
                to_add.append((columns[2], columns[4]))
            else:
                to_add.append((columns[0], columns[2]))

            for word, lemma in to_add:
                if word[0] not in ("_", "-") and lemma not in ("cla", "cln", "cld", "clr", "clar", "cldr", "çaimp") and "_" not in word:
                    column_pairs.append((word.strip(), lemma.strip()))
    return column_pairs

def extract_lemmatization_file(file_path):
    input_data = []
    with open(file_path, "r") as f:
        data = f.read().split("\n")
        for line in tqdm(data, desc=f"Loading {file_path}"):
            if not line:
              continue

            lemma, txt= line.split("\t")
            input_data.append((txt.strip(), lemma.strip()))
    return input_data

def save_dict(mydict, lang):
    byte_dict = {}
    for key, value in mydict.items():
        byte_dict[key.encode()] = [x.encode() for x in value]

    byte_dict = dict(sorted(byte_dict.items(), key=itemgetter(1)))
    filepath = f"{lang}.plzma"
    with lzma.open(filepath, "wb") as filehandle:
        pickle.dump(byte_dict, filehandle, protocol=5)


def build_lang(lang):
    data = []
    # load files
    for root, dir, files in os.walk(lang):
        for filename in files:
            path = os.path.join(root, filename)
            ext = filename.rsplit(".", 1)[-1]
            print(f"Process {path}")
            if ext == "plzma":
                data += extract_plzma(path)
            elif ext == "mlex":
                data += extract_mlex(path)
            elif ext == "txt":
                data += extract_lemmatization_file(path)
    # load from spacy
    data += get_from_spacy(f"{lang}_core_news_md")
    # Load from language
    func_name = f"new_pair_{lang}"
    func = getattr(sys.modules[__name__], func_name)
    if func:
        print(f"Call {func_name}()")
        data += func()

    # remove case
    data = [(txt.lower(), lemma.lower()) for txt, lemma in data]
    # make unique_data
    data = list(set(data))
    # sort data
    data = list(sorted(data))

    # TODO Filter
    
    # save to disk
    filename = "dictionary-%s.txt" % lang
    with open(filename, "w+") as f:
        for txt, lemma in tqdm(data, desc="Create output"):
            f.write(f"{txt}\t{lemma}\n")


    # storage = defaultdict(set)
    # for key, value in data:
    #     storage[key].add(value)
    # save_dict(storage, lang=lang)

def get_from_spacy(model):
    data = []
    # python -m spacy download fr_core_news_md
    nlp = spacy.load(model, disable=["parser", "ner"])
    vocab = list(nlp.vocab.strings)
    for word in tqdm(vocab, desc="Copy from spacy"):
        token = nlp(word)[0]
        data.append((word, token.lemma_))
    return data

def new_pair_fr():
    data = [
        ("baux", "bail"),
        ("étaient", "être"),
        ("brillante", "brillant"),
        ("brillantes", "brillant"),
        ("contente", "content"),
        ("aimante", "aimer"),
        ("chienne", "chien"),
        ("chiennes", "chien"),
        ("sorcière", "sorcier"),
        ("faille", "falloir"),
    ]
    return data

    # # remove self
    # for k,v in storage.items():
    #     if len(v) == 1 :
    #         continue
    #     if k in v:
    #         v.remove(k)
    #
    # # recursivly search for lemma
    # def reseach():
    #     last_i = 0
    #     i = -1
    #     while last_i != i:
    #         last_i = i
    #         i = 0
    #         for k,v in d.items():
    #             if len(v) == 1 :
    #                 continue
    #
    #             v2 = set()
    #             for value in v:
    #                 v2 |= d.get(value,set([]))
    #             d[k] = v2
    #             i +=1
    #
    # reseach()
    #
    # for k, v in d.items():
    #     if len(v) == 1 :
    #         continue
    #     if k in original :
    #         v2=original[k]
    #         if v2.intersection(v): # both data sourches are agree
    #             d[k] = v2
    #
    # # test "aux -> al (cheval, chevaux)"
    #
    #
    # for term, rad in (("e", ""),("es", ""), ("nne", "n"), ("nnes", "n"), ("e", "er"), ("es", "er"), ("euse", "eur"), ("euses", "eur"),("aux", "al"), ("eraient", "er"), ("erait", "er"), ("erais", "er"), ("ons", "on"),  ):
    #     for k, v in d.items():
    #         if len(v) == 1 :
    #             continue
    #         if not k.endswith(term):
    #                 continue
    #
    #         p = k[:-len(term)] + rad
    #         if p in d:
    #             d[k] = d[p]
    #             print(term, rad, k, p, v, d[k])
    #     reseach()
    #
    #
    # i = 0
    # for k,v in d.items():
    #     if len(v) == 1 :
    #         continue
    #     i += 1
    # #    print(k,v)
    # print(i)

    return storage




if __name__ == "__main__":
    lang = "fr"
    build_lang(lang)

