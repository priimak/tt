import json
from dataclasses import dataclass
from enum import StrEnum
from functools import cache
from pathlib import Path
from typing import Any, Callable, Optional

import matplotlib.pyplot as plt
import polars
from PySide6.QtCore import QRect
from PySide6.QtWidgets import QWidget
from polars import DataFrame
from pytide6 import MainWindow

from tt.data.jsonable import JsonSerializable
from tt.data.overlays import Overlay, OverlayNone, OverlaySavitzkyGolay, OverlayLowpass
from tt.gui.figure import PlotFigure


class TraceState(StrEnum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class TraceConfig:
    def __init__(self, cfg: dict):
        self.cfg = cfg

    def get_value[T](self, name: str, default_value: T) -> T:
        if name not in self.cfg:
            return default_value
        else:
            value = self.cfg[name]
            if isinstance(value, default_value.__class__):
                return value
            else:
                raise RuntimeError(f"Invalid type [{value.__class__}] for config value [{name}]")

    def get_overlay(self) -> Overlay:
        overlay_data = self.cfg.get("overlay")
        if overlay_data is None:
            return OverlayNone()
        else:
            match overlay_data.get("filter_name"):
                case "None":
                    return OverlayNone()
                case "Savitzky–Golay":
                    return OverlaySavitzkyGolay(overlay_data["window_length"], overlay_data["polyorder"])
                case "Lowpass":
                    return OverlayLowpass(overlay_data["frequency"])
                case _:
                    return OverlayNone()


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
        t = traces[trace.index]
        t._label = trace.label
        t._state = trace.state
        t.show_legend = trace.show_legend
        t.legend_location = trace.legend_location
        t.x_label = trace.x_label
        t.y_label = trace.y_label
        t.title = trace.title
        t.show_grid = trace.show_grid
        t.y_scale = trace.y_scale
        t.y_offset = trace.y_offset
        t.overlay = trace.overlay

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
        for tr in enumerate(tr_config["traces"]):
            traces.append(Trace(version = version, config = self, tcf = TraceConfig(tr[1]), index = tr[0]))
        return traces

    def get_trace_by_name(self, version: int, name: str) -> Optional["Trace"]:
        trs = [tr for tr in self.get_traces(version) if tr.name == name]
        return None if trs == [] else trs[0]

    def get_trace_by_label(self, version: int, label: str) -> Optional["Trace"]:
        trs = [tr for tr in self.get_traces(version) if tr.label == label]
        return None if trs == [] else trs[0]


class Trace(JsonSerializable):
    def __init__(self, version: int, config: TracesConfig, tcf: TraceConfig, index: int):
        self.tcf = tcf
        self.index = index
        self.__name = tcf.get_value("name", "Unknown")
        self._label = tcf.get_value("label", "Unknown")

        tr_state = tcf.get_value("state", "Active")
        self._state = TraceState.ACTIVE if tr_state == TraceState.ACTIVE.value else TraceState.INACTIVE

        self.show_legend = tcf.get_value("show_legend", False)
        self.legend_location = tcf.get_value("legend_location", "Best")
        self.x_label = self.tcf.get_value("x_label", "t")
        self.y_label = self.tcf.get_value("y_label", f"{self._label}")
        self.title = self.tcf.get_value("title", self._label)
        self.show_grid = tcf.get_value("show_grid", False)

        self.y_scale = tcf.get_value("y_scale", 1.0)
        self.y_offset = tcf.get_value("y_offset", 0.0)

        self.overlay: Overlay = tcf.get_overlay()

        self.version = version
        self.__config = config
        self.__versioned_config_file = self.__config.config_file.parent / f"{self.version:05}" / "config.json"

    def set_overlay(self, overlay: Overlay) -> None:
        self.overlay = overlay
        self.persist()

    def set_y_scale(self, y_scale: str) -> None:
        self.y_scale = float(y_scale)
        self.persist()

    def set_y_offset(self, y_offset: str) -> None:
        self.y_offset = float(y_offset)
        self.persist()

    def set_x_label(self, label: str) -> None:
        self.x_label = label
        self.persist()

    def set_y_label(self, label: str) -> None:
        self.y_label = label
        self.persist()

    def set_show_grid(self, show_grid: bool) -> None:
        self.show_grid = show_grid
        self.persist()

    def set_show_legend(self, show_legend_value: bool) -> None:
        self.show_legend = show_legend_value
        self.persist()

    def set_legend_location(self, legend_location: str) -> None:
        self.legend_location = legend_location
        self.persist()

    def set_title(self, title: str) -> None:
        self.title = title
        self.persist()

    @property
    def name(self) -> str:
        return self.__name

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.__name,
            "label": self.label,
            "state": self._state.value,
            "show_legend": self.show_legend,
            "legend_location": self.legend_location,
            "x_label": self.x_label,
            "y_label": self.y_label,
            "title": self.title,
            "show_grid": self.show_grid,
            "y_scale": self.y_scale,
            "y_offset": self.y_offset,
            "overlay": self.overlay.to_dict()
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
        return self.__t(dt, len(self.y)), [(self.y_scale * v + self.y_offset) for v in self.y]

    def show_in_new_window(self, main_window: MainWindow, super_parent: QWidget):
        main_window_geometry = main_window.geometry()
        f = PlotFigure(super_parent, self, main_window.app)  # pyright: ignore [reportAttributeAccessIssue]
        f.show()
        figure_geometry: QRect = f.geometry()
        f.move(
            main_window_geometry.center().x() - int(figure_geometry.width() / 2),
            main_window_geometry.center().y() - int(figure_geometry.height() / 2)
        )


@dataclass
class TraceDataVersioned:
    note: str


@dataclass
class TracesDataVersioned:
    trace_data: dict[str, TraceDataVersioned]


class Traces:
    def __init__(self, traces: list[Trace]):
        self.__traces = traces

    def show_in_new_window(self, show_legends: bool = True) -> None:
        fig, ax = plt.subplots()
        for trace in self.__traces:
            t, v = trace.xy
            ax.plot(t, v, "-", label = f"{trace.label} # {trace.version}")
        if show_legends:
            plt.legend(loc = "upper right")
        if fig.canvas.manager is not None:
            fig.canvas.manager.set_window_title(f"{self.__traces[0].label}")
        fig.show()
