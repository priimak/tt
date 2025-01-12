# from src.tt.data.project import TraceSource
import os
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from typing import Any

import polars as pl
from polars import DataFrame, Expr

from tt.data.jsonable import JsonSerializable
from tt.data.persistable import Persistable


class TraceSource(JsonSerializable, ABC):
    def __init__(self, persistence: Persistable):
        self.persistence = persistence  # persistence

    @abstractmethod
    def uri(self) -> str:
        pass

    @abstractmethod
    def load_data(self) -> DataFrame:
        pass

    @abstractmethod
    def has_changed(self) -> bool:
        """
        :return: Indication if source has changed in relation to the last time it was loaded
        """
        pass

    @abstractmethod
    def update_signature(self) -> None:
        """
        To be called if source has changed and data was re-loaded.
        """
        pass

    def persist(self) -> None:
        self.persistence.persist()

    def is_null_trace_source(self) -> bool:
        return isinstance(self, NullTraceSource)

    @staticmethod
    def from_config(data, persistence: Persistable) -> "TraceSource":
        match data["type"]:
            case "NullTraceSource":
                return NullTraceSource(persistence)
            case "CSVFile":
                return CSVFileTraceSource(
                    file = Path(data["path"]),
                    persistence = persistence,
                    last_modified = data["last_modified"]
                )
            case _:
                raise RuntimeError(f"Unknown trace source type: {data['type']}")


class NullTraceSource(TraceSource):
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "NullTraceSource",
        }

    def uri(self) -> str:
        return "Null"

    def has_changed(self) -> bool:
        return False

    def update_signature(self) -> None:
        pass

    def load_data(self) -> DataFrame:
        raise RuntimeError("NullTraceSource does not have any traces and cannot be loaded")

    def __eq__(self, other):
        return isinstance(other, NullTraceSource)


class CSVFileTraceSource(TraceSource):
    def __init__(self, *, file: Path, persistence: Persistable, last_modified: float | None = None):
        super().__init__(persistence)
        self.file = file
        self.last_modified = os.path.getmtime(file) if last_modified is None else last_modified

    def uri(self) -> str:
        return f"{self.file.absolute()}"

    def has_changed(self) -> bool:
        return os.path.getmtime(self.file) != self.last_modified

    def update_signature(self) -> None:
        self.last_modified = os.path.getmtime(self.file)
        self.persist()

    def load_data(self) -> DataFrame:
        text = [l for l in self.file.read_text().replace(r'\r', '').split("\n") if l != ""]
        t = [text[0]]
        header = pl.read_csv(BytesIO("\n".join(t).encode()), infer_schema = False)

        def get_ctrs() -> list[Expr]:
            if "Radix" not in text[1]:
                # second to may contain radix; if not, then add
                t.append(text[1])
                return [pl.col(cname).str.to_integer(base = 10) for cname in header.columns]
            else:
                # we have radix defined.
                columns_transform = []
                for cr in zip(header.columns, text[1].replace("Radix - ", "").split(",")):
                    cname = cr[0]  # column name
                    radix = cr[1].upper()  # radix
                    print(f"{cname} :: {radix}")
                    match radix:
                        case "HEX":
                            columns_transform.append(pl.col(cname).str.to_integer(base = 16))
                        case "OCTAL":
                            columns_transform.append(pl.col(cname).str.to_integer(base = 8))
                        case "BIN":
                            columns_transform.append(pl.col(cname).str.to_integer(base = 2))
                        case _:
                            columns_transform.append(pl.col(cname).str.to_integer())
                return columns_transform

        column_transforms = get_ctrs()
        t.extend(text[2:])
        return pl.read_csv(BytesIO("\n".join(t).encode()), infer_schema = False).with_columns(column_transforms)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "CSVFile",
            "path": f"{self.file}",
            "last_modified": self.last_modified
        }

    def __eq__(self, other):
        return isinstance(other, CSVFileTraceSource) and self.file == other.file
