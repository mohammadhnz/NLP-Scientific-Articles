import json
import os.path
import re
import time
from nltk import sent_tokenize, word_tokenize, WordNetLemmatizer
from sentence_transformers import CrossEncoder


# import nltk
# nltk.download('wordnet')
# nltk.download('omw-1.4')

class TransformersSearchEngine:
    def __init__(self):
        with open(os.path.dirname(__file__) + '/../data.json', 'r') as file:
            self.data = json.load(file)
        self.model = CrossEncoder('cross-encoder/ms-marco-TinyBERT-L-2-v2')
        self._pre_process_data()

    def _pre_process_data(self):
        self.data = [item for item in self.data if item['abstract'] is not None]
        lemm = WordNetLemmatizer()
        for item in self.data:
            doc = item['abstract']
            doc = self._remove_special_characters(doc)
            sentences = []
            for paragraph in doc.replace("\r\n", "\n").split("\n\n"):
                if len(paragraph.strip()) > 0:
                    sentences += sent_tokenize(" ".join([lemm.lemmatize(item) for item in word_tokenize(paragraph)]))
            item['abstract'] = sentences

    def _remove_special_characters(self, text):
        regex = re.compile('[^a-zA-Z0-9\s]')
        text_returned = re.sub(regex, '', text)
        return text_returned

    def query(self):
        query = input("Enter search query")
        start_time = time.time()
        scores = []
        correct_count = 0
        error_count = 0
        for item in self.data:
            if (correct_count + error_count) % 1000 == 0:
                print(str(correct_count + error_count) + " / " + str(len(self.data)))
            try:
                document = item['abstract']
                scores.append(self._get_query_score_in_doc(document, query))
                correct_count += 1
            except:
                error_count += 1
                continue
        print(correct_count)
        print(error_count)
        results = [{'title': item, 'score': score} for item, score in
                   zip([item['title'] for item in self.data], scores)]
        results = sorted(results, key=lambda x: x['score'], reverse=True)

        print("Query:", query)
        print("Search took {:.2f} seconds".format(time.time() - start_time))
        for hit in results[0:5]:
            # print("Score: {:.2f}".format(hit['score']), "\t", hit['title'])
            print(hit['title'])
        print("==========")

    def _get_query_score_in_doc(self, passages, query):
        model_inputs = [[query, passage] for passage in passages]
        scores = self.model.predict(model_inputs)
        return max(scores)


TransformersSearchEngine().query()
