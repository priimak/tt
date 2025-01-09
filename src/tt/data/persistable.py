from typing import Protocol


class Persistable(Protocol):
    def persist(self) -> None:
        ...
