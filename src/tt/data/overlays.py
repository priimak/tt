from abc import ABC, abstractmethod
from typing import Any

from scipy.signal import savgol_filter


class Overlay(ABC):
    def __init__(self, filter_name: str):
        self.filter_name = filter_name

    def to_dict(self) -> dict[str, Any]:
        return {
            "filter_name": self.filter_name
        }

    @abstractmethod
    def apply(self, x: list[float], y: list[float]) -> list[float] | None:
        pass


class OverlayNone(Overlay):
    def __init__(self):
        super().__init__("None")

    def apply(self, x: list[float], y: list[float]) -> list[float] | None:
        return None


class OverlaySavitzkyGolay(Overlay):
    __match_args__ = ("window_length", "polyorder")

    def __init__(self, window_length: str, polyorder: int):
        super().__init__("Savitzky–Golay")
        self.window_length = window_length
        self.polyorder = polyorder

        self.window_length_percentage = float(window_length.replace("%", "").strip()) \
            if window_length.endswith("%") else None
        self.window_length_points = None if window_length.endswith("%") else int(window_length)

    def set_window_length(self, window_length: str):
        self.window_length = window_length
        self.window_length_percentage = float(window_length.replace("%", "").strip()) \
            if window_length.endswith("%") else None
        self.window_length_points = None if window_length.endswith("%") else int(window_length)

    @staticmethod
    def default() -> "OverlaySavitzkyGolay":
        return OverlaySavitzkyGolay(window_length = "3%", polyorder = 2)

    def to_dict(self) -> dict[str, Any]:
        retval = super().to_dict()
        retval["window_length"] = self.window_length
        retval["polyorder"] = self.polyorder
        return retval

    def apply(self, x: list[float], y: list[float]) -> list[float] | None:
        if self.window_length_percentage is not None:
            return list(savgol_filter(
                y, window_length = int(len(x) * self.window_length_percentage / 100),
                polyorder = self.polyorder, mode = "nearest"
            ))
        elif self.window_length_points is not None:
            return list(savgol_filter(
                y, window_length = self.window_length_points, polyorder = self.polyorder, mode = "nearest"
            ))
        else:
            return None
