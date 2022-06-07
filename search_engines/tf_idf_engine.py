import json
import math
import re
import sys
from pprint import pprint

# import nltk
from typing import Union

from nltk import word_tokenize
from nltk.corpus import stopwords
# nltk.download('stopwords')
# nltk.download('punkt')


def list_to_dict(data_list: list, keys: Union[str, tuple], distinct=True) -> dict:
    data_dict = {}

    for data in data_list:
        if isinstance(keys, str):
            _key = data.get(keys)
        else:
            _key = tuple(data.get(k) for k in keys)

        _val = data

        if distinct:
            data_dict[_key] = _val
        else:
            if _key not in data_dict:
                data_dict[_key] = [_val]
            else:
                data_dict[_key].append(_val)

    return data_dict


class TF_IDF_Processor:
    def __init__(self):
        with open("../data.json", 'r') as file:
            data = json.load(file)
            self.data = list_to_dict(data, 'paperId')
        self.articles_tf_idf = dict()
        self.unique_words = set()
        self.pre_process()

    def pre_process(self):
        self._pre_process_for_tf_idf_search()

    def _remove_special_characters(self, text):
        regex = re.compile('[^a-zA-Z0-9\s]')
        text_returned = re.sub(regex, '', text)
        return text_returned

    def _prepare_text(self, text, stop_words):
        if not text:
            return []
        text = self._remove_special_characters(text)
        text = re.sub(re.compile('\d'), '', text)
        words = word_tokenize(text)
        return [word.lower() for word in words if word not in stop_words]

    def _pre_process_for_tf_idf_search(self):
        stop_words = set(stopwords.words('english'))
        articles = {}
        articles_tf = {}
        articles_idf = {}
        for key, item in self.data.items():
            words = [*self._prepare_text(item['title'], stop_words), *self._prepare_text(item['abstract'], stop_words)]
            article_map = dict.fromkeys(set(words), 0)
            tf_map = dict()
            for word in words:
                article_map[word] += 1

            for word, count in article_map.items():
                tf_map[word] = count / float(len(words))

            articles[key] = article_map
            articles_tf[key] = tf_map
            self.unique_words = self.unique_words.union(set(words))

        #idf
        N = len(articles.keys())
        for article in articles.values():
            for word, val in article.items():
                if word not in articles_idf:
                    articles_idf[word] = 0
                if val > 0:
                    articles_idf[word] += 1

        for word, val in articles_idf.items():
            articles_idf[word] = math.log(N / float(val))

        #tf idf
        for key, words_count in articles_tf.items():
            tf_idf_map = {}
            for word, count in words_count.items():
                tf_idf_map[word] = count * articles_idf[word]

            self.articles_tf_idf[key] = tf_idf_map

    def tf_idf_query(self, k=3):
        query = input('Enter your query:')
        query = word_tokenize(query)
        different_words = []
        result = []
        articles = dict.fromkeys(self.articles_tf_idf.keys(), 0)
        for word in query:
            if word.lower() != "and" and word.lower() != "or" and word.lower() != "not":
                different_words.append(word.lower())

        for search_word in set(different_words):
            if search_word in self.unique_words:
                for key, data in self.articles_tf_idf.items():
                    articles[key] += data.get(search_word, 0)

        for article, score in articles.items():
            if score > 0:
                result.append((self.data[article], score))

        result.sort(reverse=True, key=lambda x: x[1])
        return [x[0]['title'] for x in result[:k]]


pprint(TF_IDF_Processor().tf_idf_query())
