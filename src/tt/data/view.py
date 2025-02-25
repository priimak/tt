import json
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any, override

from tt.data.domain_type import DomainType


class Persisting(ABC):
    @abstractmethod
    def persist(self) -> None: ...


class AxisLean(Enum):
    LEFT = "left"
    RIGHT = "right"

    @staticmethod
    def value_of(src: str) -> "AxisLean":
        match src:
            case "left":
                return AxisLean.LEFT
            case "right":
                return AxisLean.RIGHT
            case _:
                raise ValueError(f"Unknown axis: {src}")


class TraceSpec:
    def __init__(self,
                 name: str,
                 trace_version: int,
                 on_axis: AxisLean,
                 color: str,
                 show_filtered_trace: bool,
                 show_legends: bool):
        self.__name: str = name
        self.__trace_version: int = trace_version
        self.__on_axis: AxisLean = on_axis
        self.__color: str = color  # "auto" is the default
        self._subplot: SubPlot | None = None
        self.__show_filtered_trace: bool = show_filtered_trace
        self.__show_legends: bool = show_legends

    def __repr__(self):
        return json.dumps(self.to_dic(), indent = 2)

    def to_dic(self) -> dict[str, Any]:
        return {
            "name": self.__name,
            "trace_version": self.__trace_version,
            "on_axis": self.__on_axis.value,
            "color": self.__color,
            "show_filtered_trace": self.__show_filtered_trace,
            "show_legends": self.__show_legends,
        }

    def __persist(self) -> None:
        if self._subplot is not None:
            self._subplot.persist()

    @property
    def show_legends(self) -> bool:
        return self.__show_legends

    @show_legends.setter
    def show_legends(self, value: bool) -> None:
        self.__show_legends = value
        self.__persist()

    @property
    def show_filtered_trace(self) -> bool:
        return self.__show_filtered_trace

    @show_filtered_trace.setter
    def show_filtered_trace(self, value: bool) -> None:
        self.__show_filtered_trace = value
        self.__persist()

    @property
    def name(self) -> str:
        return self.__name

    @property
    def trace_version(self) -> int:
        return self.__trace_version

    @trace_version.setter
    def trace_version(self, trace_version: int) -> None:
        self.__trace_version = trace_version
        self.__persist()

    @property
    def on_axis(self) -> AxisLean:
        return self.__on_axis

    @on_axis.setter
    def on_axis(self, on_axis: AxisLean) -> None:
        self.__on_axis = on_axis
        self.__persist()

    @property
    def color(self) -> str:
        return self.__color

    @color.setter
    def color(self, color: str) -> None:
        self.__color = color
        self.__persist()

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "TraceSpec":
        return TraceSpec(
            name = data["name"],
            trace_version = data["trace_version"],
            on_axis = AxisLean.value_of(data["on_axis"]),
            color = data["color"],
            show_filtered_trace = data.get("show_filtered_trace", False),
            show_legends = data.get("show_legends", False),
        )


class SubPlot:
    def __init__(
            self, row: int, column: int, left_axis_label: str, right_axis_label: str, show_grid: bool,
            legend_location: str, x_axis_label: str
    ):
        if row < 0:
            raise ValueError("row cannot be negative")
        if column < 0:
            raise ValueError("column cannot be negative")
        self.__row: int = row
        self.__column: int = column
        self.__traces: list[TraceSpec] = []
        self._view_spec: ViewSpec | None = None
        self.__left_axis_label: str = left_axis_label
        self.__right_axis_label: str = right_axis_label
        self.__x_axis_label: str = x_axis_label
        self.__show_grid: bool = show_grid
        self.__legend_location = legend_location

    def get_domain_type(self, project) -> DomainType | None:
        if self.__traces == []:
            return None
        else:
            trs = project.traces(-1, trace_name = self.__traces[0].name)
            return None if trs == [] else trs[0].domain_type

    def persist(self) -> None:
        if self._view_spec is not None:
            self._view_spec.persist()

    @property
    def legend_location(self) -> str:
        return self.__legend_location

    @legend_location.setter
    def legend_location(self, location: str) -> None:
        self.__legend_location = location
        self.__persist()

    def set_legend_location(self, location: str) -> None:
        self.legend_location = location

    @property
    def left_axis_label(self) -> str:
        return self.__left_axis_label

    @left_axis_label.setter
    def left_axis_label(self, label: str) -> None:
        self.__left_axis_label = label
        self.__persist()

    def set_left_axis_label(self, label: str) -> None:
        self.left_axis_label = label

    @property
    def right_axis_label(self) -> str:
        return self.__right_axis_label

    @right_axis_label.setter
    def right_axis_label(self, label: str) -> None:
        self.__right_axis_label = label
        self.__persist()

    def set_right_axis_label(self, label: str) -> None:
        self.right_axis_label = label

    @property
    def x_axis_label(self) -> str:
        return self.__x_axis_label

    @x_axis_label.setter
    def x_axis_label(self, label: str) -> None:
        self.__x_axis_label = label
        self.__persist()

    @property
    def show_grid(self) -> bool:
        return self.__show_grid

    @show_grid.setter
    def show_grid(self, value: bool) -> None:
        self.__show_grid = value
        self.__persist()

    def set_show_grid(self, value: bool) -> None:
        self.__show_grid = value

    @property
    def row(self) -> int:
        return self.__row

    @property
    def column(self) -> int:
        return self.__column

    def __repr__(self):
        return json.dumps(self.to_dic(), indent = 2)

    def to_dic(self) -> dict[str, Any]:
        return {
            "row": self.__row,
            "column": self.__column,
            "left_axis_label": self.__left_axis_label,
            "right_axis_label": self.__right_axis_label,
            "x_axis_label": self.__x_axis_label,
            "show_grid": self.__show_grid,
            "legend_location": self.__legend_location,
            "traces": [tr.to_dic() for tr in self.__traces]
        }

    def __persist(self) -> None:
        if self._view_spec is not None and self._view_spec._views is not None:
            self._view_spec._views.persist()

    def add_trace_spec(self, trace: TraceSpec) -> None:
        for t in self.__traces:
            if t.name == trace.name and t.trace_version == trace.trace_version:
                raise ValueError("Duplicate traces")
        trace._subplot = self
        self.__traces.append(trace)
        self.__persist()

    def remove_trace_spec(self, trace_name: str, trace_version: int) -> None:
        new_traces = [ts for ts in self.__traces if ts.name != trace_name or ts.trace_version != trace_version]
        self.__traces.clear()
        self.__traces.extend(new_traces)
        self.__persist()

    def get_trace_specs(self) -> list[TraceSpec]:
        return self.__traces

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "SubPlot":
        sbpl = SubPlot(
            row = data["row"],
            column = data["column"],
            left_axis_label = data.get("left_axis_label", ""),
            right_axis_label = data.get("right_axis_label", ""),
            show_grid = data.get("show_grid", False),
            legend_location = data.get("legend_location", "None"),
            x_axis_label = data.get("x_axis_label", ""),
        )

        for tr in data["traces"]:
            ts = TraceSpec.from_dict(tr)
            ts._subplot = sbpl
            sbpl.__traces.append(ts)
        return sbpl


class ViewSpec:
    def __init__(self, name: str, num_rows: int, num_columns: int, title: str):
        self.__spec_version: int = 1
        if name.strip() == "":
            raise ValueError("Name cannot be empty")
        if title.strip() == "":
            raise ValueError("Title cannot be empty")
        if num_rows <= 0:
            raise ValueError("Number of rows must be positive")
        if num_columns <= 0:
            raise ValueError("Number of columns must be positive")
        self.__name: str = name.strip()
        self.__title: str = title.strip()
        self.__num_rows: int = num_rows
        self.__num_columns: int = num_columns

        self.__sub_plots: list[SubPlot] = []
        for r in range(self.__num_rows):
            for c in range(self.__num_columns):
                sbpl = SubPlot(
                    row = r, column = c, left_axis_label = "", right_axis_label = "",
                    show_grid = False, legend_location = "None", x_axis_label = ""
                )
                sbpl._view_spec = self
                self.__sub_plots.append(sbpl)
        self._views: Views | None = None

    def persist(self) -> None:
        if self._views is not None:
            self._views.persist()

    def get_subplot(self, row: int, column: int) -> SubPlot:
        if row < 0 or row >= self.__num_rows or column < 0 or column >= self.__num_columns:
            raise ValueError("Invalid row or column")
        else:
            for spl in self.__sub_plots:
                if spl.row == row and spl.column == column:
                    return spl
            raise ValueError(f"Unable to find subplot at [{row}, {column}]")

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str) -> None:
        if self.__name == name:
            return
        elif self._views is not None and name in self._views.get_view_spec_names():
            raise ValueError(f"View [{name}] already exists")
        else:
            self.__name = name
            if self._views is not None:
                self._views.persist()

    @property
    def title(self) -> str:
        return self.__title

    @title.setter
    def title(self, title: str) -> None:
        if self.__name == title:
            return
        else:
            self.__title = title
            if self._views is not None:
                self._views.persist()

    # def __recreate_subplots(self) -> None:
    #     new_sub_plots = []
    #     for r in range(self.__num_rows):
    #         for c in range(self.__num_columns):
    #             sbpl = [s for s in self.__sub_plots if s.row == r and s.column == c]
    #             if sbpl != []:
    #                 new_sub_plots.extend(sbpl)
    #             else:
    #                 sbpl = SubPlot(row = r, column = c)
    #                 sbpl._view_spec = self
    #                 new_sub_plots.append(sbpl)
    #     self.__sub_plots.clear()
    #     self.__sub_plots.extend(new_sub_plots)
    #     if self._views is not None:
    #         self._views.persist()

    @property
    def num_rows(self) -> int:
        return self.__num_rows

    # @num_rows.setter
    # def num_rows(self, num_rows: int) -> None:
    #     self.__num_rows = num_rows
    #     self.__recreate_subplots()

    @property
    def num_columns(self) -> int:
        return self.__num_columns

    # @num_columns.setter
    # def num_columns(self, num_columns: int) -> None:
    #     self.__num_columns = num_columns
    #     self.__recreate_subplots()

    def to_dic(self) -> dict[str, Any]:
        return {
            "spec_version": self.__spec_version,
            "title": self.__title,
            "view_name": self.__name,
            "num_rows": self.__num_rows,
            "num_columns": self.__num_columns,
            "sub_plots": [spl.to_dic() for spl in self.__sub_plots]
        }

    def __repr__(self):
        return json.dumps(self.to_dic(), indent = 2)

    @staticmethod
    def from_dict(data: dict) -> "ViewSpec":
        spec_version = data["spec_version"]
        if spec_version != 1:
            raise RuntimeError(f"Unable to parse ViewSpec version {spec_version}")
        else:
            vs = ViewSpec(
                name = data["view_name"],
                num_rows = data["num_rows"],
                num_columns = data["num_columns"],
                title = data["title"],
            )
            vs.__sub_plots.clear()
            for sp_data in data["sub_plots"]:
                sbpl = SubPlot.from_dict(sp_data)
                sbpl._view_spec = vs
                vs.__sub_plots.append(sbpl)
            return vs


class Views(Persisting):
    def __init__(self, views: list[ViewSpec] | None = None):
        self.__views: list[ViewSpec] = [] if views is None else views
        self.__source_file: Path | None = None

    def __repr__(self):
        return json.dumps(self.__to_list(), indent = 2)

    def __to_list(self) -> list[Any]:
        return [v.to_dic() for v in self.__views]

    @override
    def persist(self, dst_file: Path | None = None) -> None:
        file = self.__source_file if dst_file is None else dst_file
        self.__source_file = file
        if self.__source_file is not None:
            self.__source_file.write_text(json.dumps(self.__to_list(), indent = 2))

    @staticmethod
    def from_json(src: str) -> "Views":
        data = json.loads(src)
        views_specs = []
        for view_spec_data in data:
            views_specs.append(ViewSpec.from_dict(view_spec_data))
        views = Views(views_specs)
        for vs in views_specs:
            vs._views = views
        return views

    @staticmethod
    def from_json_file(file: Path) -> "Views":
        if not file.exists():
            file.write_text(json.dumps([]))

        views = Views.from_json(file.read_text())
        views.__source_file = file
        return views

    def get_view_spec_names(self) -> list[str]:
        return [v.name for v in self.__views]

    def add_view_spec(self, vs: ViewSpec) -> ViewSpec:
        if vs.name in self.get_view_spec_names():
            raise RuntimeError(f"View [{vs.name}] already exists")
        else:
            self.__views.append(vs)
            self.persist()
            vs._views = self
            return vs

    def get_view_spec(self, name: str) -> ViewSpec | None:
        for v in self.__views:
            if v.name == name:
                return v
        return None

    def delete_view(self, view_name: str) -> None:
        index_to_delete = [iv[0] for iv in enumerate(self.__views) if iv[1].name == view_name]
        if index_to_delete != []:
            del self.__views[index_to_delete[0]]
            self.persist()
