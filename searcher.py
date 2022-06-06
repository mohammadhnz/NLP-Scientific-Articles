from pprint import pprint
from typing import List

from search_engines.base_search_engine import BaseSearchEngine
from search_engines.boolean_search_engine import BooleanSearchEngine
from search_engines.transformer_engine import TransformersSearchEngine


class Searcher:
    def __init__(self):
        self.engines: List[BaseSearchEngine] = [
            BooleanSearchEngine(),
            TransformersSearchEngine()
        ]

    def execute(self):
        query = input("Enter query or Enter 'exit' to exit.")
        while query.lower() != "exit":
            results = dict()
            for engine in self.engines:
                results[engine.engine_type] = engine.query(query)
            pprint(results)
            query = input("Enter query or Enter 'exit' to exit.")


Searcher().execute()
