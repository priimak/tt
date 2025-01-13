import json
from dataclasses import dataclass
from enum import StrEnum
from functools import cache
from pathlib import Path
from typing import Any, Callable, Optional

import matplotlib.pyplot as plt
import polars
from polars import DataFrame

from tt.data.jsonable import JsonSerializable


class TraceState(StrEnum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class TracesConfig(JsonSerializable):
    def __init__(self, config_file: Path, latest_traces_version: int, dt: Callable[[], float]):
        self.config_file = config_file
        self.latest_traces_version = latest_traces_version
        self.traces: list[Trace] = []
        self.dt = dt

    @cache
    def df(self, version: int) -> DataFrame:
        return polars.read_parquet(self.config_file.parent / f"{version:05}" / "traces.parquet.lz4")

    def to_dict(self) -> dict[str, Any]:
        return {"traces": [t.to_dict() for t in self.traces]}

    def persist(self) -> None:
        self.config_file.write_text(self.to_json())

    def save(self, trace: "Trace") -> None:
        traces = self.get_traces(-1)
        for t in traces:
            if t.name == trace.name:
                t._label = trace.label
                t._state = trace.state
        self.config_file.write_text(json.dumps({
            "traces": [t.to_dict() for t in traces]
        }, indent = 2))

    def get_traces(self, version: int) -> list["Trace"]:
        if version == 0:
            return []

        version = (self.latest_traces_version + 1 + version) if version < 0 else version
        if version > self.latest_traces_version or version == 0:
            return []

        tr_config = json.loads(self.config_file.read_text())
        traces = []
        for tr in tr_config["traces"]:
            state = TraceState.ACTIVE if tr["state"] == TraceState.ACTIVE.value else TraceState.INACTIVE
            traces.append(
                Trace(name = tr["name"], label = tr["label"], state = state, version = version, config = self)
            )
        return traces

    def get_trace_by_name(self, version: int, name: str) -> Optional["Trace"]:
        trs = [tr for tr in self.get_traces(version) if tr.name == name]
        return None if trs == [] else trs[0]

    def get_trace_by_label(self, version: int, label: str) -> Optional["Trace"]:
        trs = [tr for tr in self.get_traces(version) if tr.label == label]
        return None if trs == [] else trs[0]


class Trace(JsonSerializable):
    def __init__(self, name: str, label: str, state: TraceState, version: int, config: TracesConfig):
        self.__name = name
        self._label = label
        self._state = state
        self.version = version
        self.__config = config
        self.__versioned_config_file = self.__config.config_file.parent / f"{self.version:05}" / "config.json"

    @property
    def name(self) -> str:
        return self.__name

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.__name,
            "label": self.label,
            "state": self._state.value,
        }

    def __repr__(self):
        as_dict = self.to_dict()
        as_dict["version"] = self.version
        return json.dumps(as_dict, indent = 2)

    def persist(self) -> None:
        self.__config.save(self)

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, label: str) -> None:
        if self._label != label:
            if self.__config.get_trace_by_label(self.version, label) is not None:
                raise RuntimeError("Trace with such a label already exists")
            else:
                self._label = label
                self.persist()

    @property
    def state(self) -> TraceState:
        return self._state

    @state.setter
    def state(self, state: TraceState) -> None:
        self._state = state
        self.persist()

    @property
    def note(self) -> str:
        return json.loads(self.__versioned_config_file.read_text())[self.__name]["note"]

    @note.setter
    def note(self, note: str) -> None:
        data = json.loads(self.__versioned_config_file.read_text())
        data[self.__name]["note"] = note
        self.__versioned_config_file.write_text(json.dumps(data, indent = 2))

    @property
    @cache
    def y(self) -> list[float]:
        df: DataFrame = self.__config.df(self.version)
        return df.get_column(self.name).to_list()

    @cache
    def __t(self, dt: float, len: int) -> list[float]:
        return [dt * i for i in range(len)]

    @property
    def xy(self) -> tuple[list[float], list[float]]:
        dt = self.__config.dt()
        return self.__t(dt, len(self.y)), self.y

    def show_in_new_window(self):
        fig, ax = plt.subplots()
        t, v = self.xy
        ax.plot(t, v, "-")
        plt.show()


@dataclass
class TraceDataVersioned:
    note: str


@dataclass
class TracesDataVersioned:
    trace_data: dict[str, TraceDataVersioned]
