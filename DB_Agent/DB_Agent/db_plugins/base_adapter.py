# db_plugins/base_adapter.py
from abc import ABC, abstractmethod

class BaseDBAdapter(ABC):
    @abstractmethod
    def get_schema_metadata(self) -> dict:
        pass

    @abstractmethod
    def execute_query(self, query: str) -> list[dict]:
        pass
