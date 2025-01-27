import json
from dataclasses import dataclass
from enum import Enum
from typing import Any


class AxisLean(Enum):
    LEFT = "left"
    RIGHT = "right"


@dataclass
class TraceSpec:
    trace_name: str
    trace_version: int
    on_axis: AxisLean

    def to_dic(self) -> dict[str, Any]:
        return {
            "trace_name": self.trace_name,
            "trace_version": self.trace_version,
            "on_axis": self.on_axis.value,
        }


@dataclass
class SubPlot:
    row: int
    column: int
    traces: list[TraceSpec]

    def to_dic(self) -> dict[str, Any]:
        return {
            "row": self.row,
            "column": self.column,
            "traces": [tr.to_dic() for tr in self.traces]
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "SubPlot":
        return SubPlot(
            row = data["row"],
            column = data["column"],
            traces = []
        )


@dataclass
class ViewSpec:
    spec_version: int
    view_name: str
    num_rows: int
    num_columns: int
    sub_plots: list[SubPlot]

    def to_dic(self) -> dict[str, Any]:
        return {
            "spec_version": self.spec_version,
            "view_name": self.view_name,
            "num_rows": self.num_rows,
            "num_columns": self.num_columns,
            "sub_plots": [spl.to_dic() for spl in self.sub_plots]
        }

    @staticmethod
    def from_dict(data: dict) -> "ViewSpec":
        spec_version = data["spec_version"]
        if spec_version != 1:
            raise RuntimeError(f"Unable to parse ViewSpec version {spec_version}")
        else:
            return ViewSpec(
                spec_version = spec_version,
                view_name = data["view_name"],
                num_rows = data["num_rows"],
                num_columns = data["num_columns"],
                sub_plots = []
            )


@dataclass
class Views:
    views: list[ViewSpec]

    def to_list(self) -> list[Any]:
        return [v.to_dic() for v in self.views]

    @staticmethod
    def from_json(src: str) -> "Views":
        data = json.loads(src)
        views = []
        for view_spec_data in data:
            views.append(ViewSpec.from_dict(view_spec_data))
        return Views(views)

# if __name__ == '__main__':
#     a = ViewSpec(spec_version = 1, view_name = "xyz", num_rows = 2, num_columns = 3, sub_plots = [
#         SubPlot(row = 1, column = 1,
#                 traces = [TraceSpec(trace_name = "foo", trace_version = -1, on_axis = AxisLean.LEFT)]),
#         SubPlot(row = 2, column = 1, traces = []),
#     ])
#     # print(json.dumps(a.to_dic(), indent = 2))
#     vs = Views(views = [a])
#     jdata = json.dumps(vs.to_list(), indent = 2)
#     print(jdata)
#
#     data = json.loads(jdata)
#     print(data)
#     b = Views.from_json(jdata)
#     print(b)
#     # import matplotlib.pyplot as plt
#     #
#     # from matplotlib.gridspec import GridSpec
#     #
#     #
#     # def format_axes(fig):
#     #     for i, ax in enumerate(fig.axes):
#     #         ax.text(0.5, 0.5, "ax%d" % (i + 1), va = "center", ha = "center")
#     #         # ax.tick_params(labelbottom = False, labelleft = False)
#     #
#     #
#     # fig = plt.figure(layout = "constrained")
#     #
#     # # gs = GridSpec(3, 3, figure = fig, wspace = 0.025, hspace = 0.25, height_ratios = [0.1, 0.2, 0.7])
#     # gs = GridSpec(3, 3, figure = fig, wspace = 0.025, hspace = 0.025)
#     # gs_ = gs[0, slice(0, 3)]
#     # ax1 = fig.add_subplot(gs_)
#     #
#     # # identical to ax1 = plt.subplot(gs.new_subplotspec((0, 0), colspan=3))
#     # # ax2 = fig.add_subplot(gs[1, :-1])
#     # ax2: Axes = fig.add_subplot(gs[1, 0:3])
#     # ax1.set_xticks([])
#     # ax2.set_xticks([])
#     # ax3 = fig.add_subplot(gs[2, 0:3])
#     # # ax4 = fig.add_subplot(gs[-1, 0])
#     # # ax5 = fig.add_subplot(gs[-1, -2])
#     #
#     # ax1.set_aspect('equal')
#     # ax2.set_aspect('equal')
#     # ax3.set_aspect('equal')
#     # # fig.suptitle("GridSpec")
#     # format_axes(fig)
#     #
#     # plt.show()
