import json
from collections import defaultdict

import nltk
import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# nltk.download("punkt")

class Article(db.Model):
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)
    abstract = db.Column(db.String)
    author_names = db.relationship('Author', backref='article')


class Author(db.Model):
    __tablename__ = 'author'
    name = db.Column(db.String, primary_key=True)
    key = db.Column(db.String, primary_key=True)
    parent_id = db.Column(db.String, db.ForeignKey("article.id"))


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
    db.create_all()
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

    def _pre_process_for_boolean_search(self):
        total_words = defaultdict(list)
        total_count = len(self.data)
        counter = 0
        for item in self.data:
            print(round(counter/total_count, 2))
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
