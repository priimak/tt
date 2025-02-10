from abc import abstractmethod
from functools import reduce
from operator import mul
from typing import Any

from scipy import signal

from tt.data.punits import Frequency, Duration


class Function:
    def __init__(self, project, derivative_sources: list[str]):
        from tt.data.project import Project
        self.project: Project = project
        self.source_traces = derivative_sources

    @abstractmethod
    def xy(self, trace_version: int) -> tuple[list[float], list[float]]:
        pass

    def to_dict(self) -> dict[str, Any]:
        return {
            "derivative_function": self.name(),
            "derivative_params": self.params(),
            "derivative_sources": self.source_traces,
        }

    @abstractmethod
    def name(self) -> str:
        pass

    def derivative_sources(self) -> list[str]:
        return self.source_traces

    def params(self) -> dict[str, Any]:
        return {}


class Functions:
    @staticmethod
    def from_json(data: dict[str, Any], project) -> Function | None:
        derivative_function = data.get("derivative_function", "")
        match derivative_function:
            case "":
                return None
            case "add":
                return Functions.Add(project, data.get("derivative_sources", []))
            case "subtract":
                return Functions.Subtract(project, data.get("derivative_sources", []))
            case "multiply":
                return Functions.Multiply(project, data.get("derivative_sources", []))
            case "divide":
                return Functions.Divide(project, data.get("derivative_sources", []))
            case "lowpass_filter":
                return Functions.LowpassFilter(
                    project,
                    data.get("derivative_sources", []),
                    cutoff_frequency = Frequency.value_of(data["derivative_params"]["cutoff_frequency"])
                )
            case _:
                raise ValueError(f"Unknown derivative function [{derivative_function}]")

    @staticmethod
    def value_of(project, function_name: str, source_traces: list[str], params: dict[str, Any]) -> Function:
        match function_name:
            case "add":
                return Functions.Add(project, source_traces)
            case "subtract":
                return Functions.Subtract(project, source_traces)
            case "multiply":
                return Functions.Multiply(project, source_traces)
            case "divide":
                return Functions.Divide(project, source_traces)
            case "lowpass_filter":
                return Functions.LowpassFilter(project, source_traces, Frequency.value_of(params["cutoff_frequency"]))
            case _:
                raise ValueError(f"Unknown function [{function_name}]")

    NAMES = ["Add", "Subtract", "Multiply", "Divide", "Lowpass Filter"]
    CONF_NAMES_2_NAME = {
        "add": "Add",
        "subtract": "Subtract",
        "multiply": "Multiply",
        "divide": "Divide",
        "lowpass_filter": "Lowpass Filter"
    }

    class Add(Function):
        def __init__(self, project, source_traces: list[str]):
            super().__init__(project, source_traces)

        def xy(self, trace_version: int) -> tuple[list[float], list[float]]:
            from tt.data.trace import Trace
            traces: list[Trace] = [
                self.project.traces(version = trace_version, trace_name = trace_name)[0]
                for trace_name in self.source_traces
            ]
            ys: list[list[float]] = [t.y(self.project) for t in traces]

            return traces[0].x(self.project), [sum(z) for z in zip(*ys)]

        def name(self) -> str:
            return "add"

    class Subtract(Function):
        def __init__(self, project, source_traces: list[str]):
            super().__init__(project, source_traces)
            if len(source_traces) != 2:
                raise ValueError("Subtract only supports 2 traces")

        def xy(self, trace_version: int) -> tuple[list[float], list[float]]:
            trace0 = self.project.traces(version = trace_version, trace_name = self.source_traces[0])[0]
            trace1 = self.project.traces(version = trace_version, trace_name = self.source_traces[1])[0]
            return trace0.x(self.project), [t[0] - t[1] for t in zip(trace0.y(self.project), trace1.y(self.project))]

        def name(self) -> str:
            return "subtract"

    class Multiply(Function):
        def __init__(self, project, source_traces: list[str]):
            super().__init__(project, source_traces)

        def xy(self, trace_version: int) -> tuple[list[float], list[float]]:
            from tt.data.trace import Trace
            traces: list[Trace] = [
                self.project.traces(version = trace_version, trace_name = trace_name)[0]
                for trace_name in self.source_traces
            ]
            ys: list[list[float]] = [t.y(self.project) for t in traces]

            return traces[0].x(self.project), [reduce(mul, z) for z in zip(*ys)]

        def name(self) -> str:
            return "multiply"

    class Divide(Function):
        def __init__(self, project, source_traces: list[str]):
            super().__init__(project, source_traces)
            if len(source_traces) != 2:
                raise ValueError("Divide only supports 2 traces")

        def xy(self, trace_version: int) -> tuple[list[float], list[float]]:
            trace0 = self.project.traces(version = trace_version, trace_name = self.source_traces[0])[0]
            trace1 = self.project.traces(version = trace_version, trace_name = self.source_traces[1])[0]
            return trace0.x(self.project), [t[0] / t[1] for t in zip(trace0.y(self.project), trace1.y(self.project))]

        def name(self) -> str:
            return "divide"

    class LowpassFilter(Function):
        def __init__(self, project, source_traces: list[str], cutoff_frequency: Frequency):
            super().__init__(project, source_traces)
            if len(source_traces) != 1:
                raise ValueError("LowpassFilter only supports one input trace")

            self.cutoff_frequency = cutoff_frequency

        def xy(self, trace_version: int) -> tuple[list[float], list[float]]:
            dt = Duration.value_of(f"{self.project.implied_dt} {self.project.dt_unit}")
            fs = (1 / dt).as_float("Hz")
            fc = self.cutoff_frequency.as_float("Hz")
            w1 = fc / (fs / 2)

            x, y = self.project.traces(version = trace_version, trace_name = self.source_traces[0])[0].xy(self.project)
            b, a = signal.butter(N = 10, Wn = w1, btype = "lowpass", analog = False)
            return x, list(signal.filtfilt(b, a, y))

        def name(self) -> str:
            return "lowpass_filter"

        def params(self) -> dict[str, Any]:
            return {"cutoff_frequency": f"{self.cutoff_frequency}"}
