import json
import re

import fasttext
import numpy as np
from nltk import sent_tokenize
from sklearn.metrics.pairwise import cosine_similarity

from search_engines.base_search_engine import BaseSearchEngine
from search_engines.tf_idf_engine import list_to_dict


class WORDEMBEDDINGProcessor(BaseSearchEngine):

    def __init__(self):
        with open("../data.json", 'r') as file:
            data = json.load(file)
            self.data = list_to_dict(data, 'paperId')

        self.model = None
        self.average_vector = None
        self.articles = []
        self._pre_process()

    def find_k_most_relevant(self, query_similarity_vector, k):
        results = []
        for i in range(k):
            max_value = max(query_similarity_vector)
            max_index = query_similarity_vector.index(max_value)
            results.append(self.articles[max_index])
            query_similarity_vector[max_index] = -1
        return results

    def calculate_average_vector(self, article):
        all_tokens = article.split(' ')
        tokens_vectors = []
        for word in all_tokens:
            tokens_vectors.append(self.model.get_word_vector(word))

        return np.mean(np.array(tokens_vectors), axis=0)

    def calculate_all_average_vectors(self):
        average_vectors = []
        for article in self.articles:
            average_vectors.append(self.calculate_average_vector(article))

        return average_vectors

    def _pre_process(self):
        self._pre_process_for_word_embedding_search()

    def _remove_special_characters(self, text):
        regex = re.compile('[^a-zA-Z0-9\s]')
        text_returned = re.sub(regex, '', text)
        return text_returned

    def _prepare_text(self, text):
        if not text:
            return []
        text = self._remove_special_characters(text)
        text = re.sub(re.compile('\d'), '', text)
        sentences = sent_tokenize(text)
        return [sentence.lower() for sentence in sentences]

    def prepare_query(self, query):
        if not query:
            return ''

        query = self._remove_special_characters(query)
        return re.sub(re.compile('\d'), '', query)

    def _pre_process_for_word_embedding_search(self):
        for key, item in self.data.items():
            sentences = self._prepare_text(item['abstract'])
            self.articles += sentences

        # with open('articles_all.txt', mode='wt', encoding='utf-8') as f:
        #     f.write('\n'.join(self.articles))
        # self.model = fasttext.train_unsupervised('articles_all.txt')
        # self.model.save_model('articles_model.bin')
        self.model = fasttext.load_model('articles_model.bin')
        # self.average_vector = self.calculate_all_average_vectors()
        # np.save('articles_average_vector', self.average_vector)
        self.average_vector = np.load('articles_average_vector.npy')


    def query(self, query, k=5):
        query = self.prepare_query(query)
        query_vector = self.calculate_average_vector(query)
        query_similarity_vector = cosine_similarity(
            [query_vector],
            self.average_vector
        )
        query_similarity_vector = list(query_similarity_vector[0])
        return self.find_k_most_relevant(query_similarity_vector, k)


if __name__ == '__main__':
    a = WORDEMBEDDINGProcessor()
    print(a.query('preprocessing data'))
