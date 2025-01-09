import json
from abc import ABC, abstractmethod
from typing import Any


class JsonSerializable(ABC):
    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def persist(self) -> None:
        pass

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent = 2)

    def __repr__(self):
        d = self.to_dict()
        d["class"] = self.__class__.__name__
        return json.dumps(d, indent = 2)
