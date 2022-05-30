import json
import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)
    abstract = db.Column(db.String)
    author_names = db.relationship('Author', backref='article')


class Author(db.Model):
    __tablename__ = 'author'
    name = db.Column(db.String, primary_key=True)
    key = db.Column(db.String, primary_key=True)
    parent_id = db.Column(db.String, db.ForeignKey("article.id"))


if __name__ == '__main__':
    db.create_all()
    result = requests.get(
        'http://api.semanticscholar.org/graph/v1/paper/search?query=literature+graph&limit=100&fields=title,authors,abstract')
    json_ob = json.loads(result.text)
    articles = []
    data_list = json_ob['data']
    for i in range(100):
        paper_id = data_list[i]['paperId']
        paper_title = data_list[i]['title']
        paper_abstract = data_list[i]['abstract']
        paper_author_list = data_list[i]['authors']
        authors = []
        for author in paper_author_list:
            au = Author(key=author['authorId'] + paper_id, parent_id=paper_id, name=author['name'])
            db.session.add(au)
            db.session.commit()
        ar = Article(id=paper_id, title=paper_title, abstract=paper_abstract)
        db.session.add(ar)
        db.session.commit()
    for user in db.session.query(Article):
        print(type(user), user.id, user.title)
