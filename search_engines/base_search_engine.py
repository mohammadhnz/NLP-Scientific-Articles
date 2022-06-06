from abc import abstractmethod


class BaseSearchEngine:
    engine_type = "default"

    class Meta:
        abstract = True

    @abstractmethod
    def query(self, query):
        pass

    @abstractmethod
    def _pre_process(self):
        pass

    def get_engine_type(self):
        return self.engine_type
