import json
import os.path
import re
import sys
from collections import defaultdict
from pprint import pprint

from nltk import word_tokenize
from nltk.corpus import stopwords

# import nltk
# nltk.download('stopwords')
from search_engines.base_search_engine import BaseSearchEngine


class Node:
    def __init__(self, docId, freq=None):
        self.freq = freq
        self.doc = docId
        self.nextval = None


class SlinkedList:
    def __init__(self, head=None):
        self.head = head


class BooleanSearchEngine(BaseSearchEngine):
    engine_type = "boolean retrieval"

    def __init__(self):
        with open(os.path.dirname(__file__) + '/../data.json', 'r') as file:
            self.data = json.load(file)
        self.articles = dict()
        self._pre_process()

    def _pre_process(self):
        self._pre_process_for_boolean_search()

    def _finding_all_unique_words_and_freq(self, words):
        return {word: words.count(word) for word in list(set(words))}

    def _remove_special_characters(self, text):
        regex = re.compile('[^a-zA-Z0-9\s]')
        text_returned = re.sub(regex, '', text)
        return text_returned

    def _pre_process_for_boolean_search(self):
        stop_words = set(stopwords.words('english'))
        total_words = defaultdict(list)
        total_count = len(self.data)
        counter = 0
        linked_list_data = {}
        all_words = {}
        for item in self.data:
            text = item['title']
            authors = item['authors']
            for auther in authors:
                text += " " + auther['name']
            text = self._remove_special_characters(text)
            text = re.sub(re.compile('\d'), '', text)
            words = word_tokenize(text)
            words = [word.lower() for word in words if len(words) > 1 and word not in stop_words]
            all_words.update(self._finding_all_unique_words_and_freq(words))
        self.unique_words_all = list(set(all_words.keys()))

        linked_list_data = {}
        for word in self.unique_words_all:
            linked_list_data[word] = SlinkedList()
            linked_list_data[word].head = Node(1, Node)
        word_freq_in_doc = {}
        idx = 1
        for item in self.data:
            text = item['title']
            authors = item['authors']
            for auther in authors:
                text += " " + auther['name']
            text = self._remove_special_characters(text)
            text = re.sub(re.compile('\d'), '', text)
            words = word_tokenize(text)
            words = [word.lower() for word in words if len(words) > 1 and word not in stop_words]
            word_freq_in_doc = self._finding_all_unique_words_and_freq(words)
            for word in word_freq_in_doc.keys():
                linked_list = linked_list_data[word].head
                while linked_list.nextval is not None:
                    linked_list = linked_list.nextval
                linked_list.nextval = Node(idx, word_freq_in_doc[word])
            self.articles[idx] = item
            idx = idx + 1
        self.linked_list_data = linked_list_data

    def query(self, query):
        query = word_tokenize(query)
        connecting_words = []
        cnt = 1
        different_words = []
        for word in query:
            if word.lower() != "and" and word.lower() != "or" and word.lower() != "not":
                different_words.append(word.lower())
            else:
                connecting_words.append(word.lower())
        total_articles = len(self.articles.keys())
        zeroes_and_ones = []
        zeroes_and_ones_of_all_words = []
        for word in different_words:
            if word.lower() in self.unique_words_all:
                zeroes_and_ones = [0] * total_articles
                linkedlist = self.linked_list_data[word].head
                # print(word)
                while linkedlist.nextval is not None:
                    zeroes_and_ones[linkedlist.nextval.doc - 1] = 1
                    linkedlist = linkedlist.nextval
                zeroes_and_ones_of_all_words.append(zeroes_and_ones)
            else:
                # print(word, " not found")
                sys.exit()
        # print(zeroes_and_ones_of_all_words)
        for word in connecting_words:
            word_list1 = zeroes_and_ones_of_all_words[0]
            word_list2 = zeroes_and_ones_of_all_words[1]
            if word == "and":
                bitwise_op = [w1 & w2 for (w1, w2) in zip(word_list1, word_list2)]
                zeroes_and_ones_of_all_words.remove(word_list1)
                zeroes_and_ones_of_all_words.remove(word_list2)
                zeroes_and_ones_of_all_words.insert(0, bitwise_op);
            elif word == "or":
                bitwise_op = [w1 | w2 for (w1, w2) in zip(word_list1, word_list2)]
                zeroes_and_ones_of_all_words.remove(word_list1)
                zeroes_and_ones_of_all_words.remove(word_list2)
                zeroes_and_ones_of_all_words.insert(0, bitwise_op);
            elif word == "not":
                bitwise_op = [not w1 for w1 in word_list2]
                bitwise_op = [int(b == True) for b in bitwise_op]
                zeroes_and_ones_of_all_words.remove(word_list2)
                zeroes_and_ones_of_all_words.remove(word_list1)
                bitwise_op = [w1 & w2 for (w1, w2) in zip(word_list1, bitwise_op)]
        # zeroes_and_ones_of_all_words.insert(0, bitwise_op);

        articles = []
        lis = zeroes_and_ones_of_all_words[0]
        cnt = 1
        for index in lis:
            if index == 1:
                articles.append(self.articles[cnt])
            cnt = cnt + 1
        return [item['title'] for item in articles[:5]]

