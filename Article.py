from sqlalchemy import Column, Integer, Unicode, UnicodeText, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:////tmp/teste.db', echo=True)
Base = declarative_base(bind=engine)


class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    title = Column(Unicode(40))
    #author_name = Column(UnicodeText, nullable=True)
    abstract = Column(String(20))

    def __init__(self, id, title, abstract):
        self.id = id
        self.title = title
        #self.author_name = author_name
        self.abstract = abstract


Base.metadata.create_all()

Session = sessionmaker(bind=engine)
s = Session()
