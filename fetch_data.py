import json
import re
from collections import defaultdict

import nltk
import requests


def get_data_from_api():
    urls = [
        f'http://api.semanticscholar.org/graph/v1/paper/search?query=nlp+transformer&offset={offset}&limit=100&fields=title,authors,abstract'
        for offset in range(0, 5000, 100)
    ]
    total_data = []
    for url in urls:
        try:
            result = requests.get(url)
            json_ob = json.loads(result.text)
            total_data += json_ob['data']
        except Exception as e:
            print("failted", url)
            continue
    return total_data


def initalize():
    articles = []
    data_list = get_data_from_api()
    print(len(data_list))
    with open("data.json", 'w') as file:
        file.write(json.dumps(data_list))


class PreProcessor:
    def __init__(self):
        with open("data.json", 'r') as file:
            self.data = json.load(file)

    def pre_process(self):
        self._pre_process_for_boolean_search()

    def _finding_all_unique_words_and_freq(words):
        words_unique = []
        word_freq = {}
        for word in words:
            if word not in words_unique:
                words_unique.append(word)
        for word in words_unique:
            word_freq[word] = words.count(word)
        return word_freq

    def _finding_freq_of_word_in_doc(word, words):
        freq = words.count(word)

    def _remove_special_characters(text):
        regex = re.compile('[^a-zA-Z0-9\s]')
        text_returned = re.sub(regex, '', text)
        return text_returned

    def _pre_process_for_boolean_search(self):
        total_words = defaultdict(list)
        total_count = len(self.data)
        counter = 0
        for item in self.data:
            print(round(counter / total_count, 2))
            counter += 1
            title = item['title']
            authors = item['authors']
            words = nltk.word_tokenize(title)
            for auther in authors:
                words += nltk.word_tokenize(auther['name'])
            for word in words:
                total_words[word].append(item['paperId'])

        with open("authers_and_title_boolean.json", 'w') as file:
            file.write(json.dumps(total_words, indent=4))


PreProcessor().pre_process()
