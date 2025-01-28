from enum import Enum
from typing import Any


class FrequencyUnit(Enum):
    THz = "THz"
    GHz = "GHz"
    MHz = "MHz"
    KHz = "KHz"
    Hz = "Hz"

    def period_in_seconds(self) -> float:
        match self:
            case FrequencyUnit.Hz:
                return 1
            case FrequencyUnit.KHz:
                return 0.001
            case FrequencyUnit.MHz:
                return 1e-6
            case FrequencyUnit.GHz:
                return 1e-9
            case FrequencyUnit.THz:
                return 1e-12
            case _:
                raise RuntimeError("Invalid frequency unit")

    @staticmethod
    def value_of(src: Any) -> "FrequencyUnit":
        if isinstance(src, FrequencyUnit):
            return src
        elif isinstance(src, str):
            match src.strip().lower():
                case "thz":
                    return FrequencyUnit.THz
                case "ghz":
                    return FrequencyUnit.GHz
                case "mhz":
                    return FrequencyUnit.MHz
                case "khz":
                    return FrequencyUnit.KHz
                case "hz":
                    return FrequencyUnit.Hz
                case _:
                    raise ValueError(f"Unknown frequency unit: {src}")
        else:
            raise ValueError(f"Unknown frequency unit: {src}")

    def matching_time_unit(self) -> "TimeUnit":
        match self:
            case FrequencyUnit.Hz:
                return TimeUnit.s
            case FrequencyUnit.KHz:
                return TimeUnit.ms
            case FrequencyUnit.MHz:
                return TimeUnit.us
            case FrequencyUnit.GHz:
                return TimeUnit.ns
            case FrequencyUnit.THz:
                return TimeUnit.ps


class Frequency:
    def __init__(self, freq: float, unit: FrequencyUnit):
        self.__freq = freq
        self.__unit = unit

    @staticmethod
    def value_of(src: Any) -> "Frequency":
        if isinstance(src, Frequency):
            return src
        elif isinstance(src, str):
            src_clean = src.strip().lower()
            if src_clean.endswith("thz"):
                return Frequency(float(src_clean.replace("thz", "")), FrequencyUnit.THz)
            elif src_clean.endswith("ghz"):
                return Frequency(float(src_clean.replace("ghz", "")), FrequencyUnit.GHz)
            elif src_clean.endswith("mhz"):
                return Frequency(float(src_clean.replace("mhz", "")), FrequencyUnit.MHz)
            elif src_clean.endswith("khz"):
                return Frequency(float(src_clean.replace("khz", "")), FrequencyUnit.KHz)
            elif src_clean.endswith("hz"):
                return Frequency(float(src_clean.replace("hz", "")), FrequencyUnit.Hz)
            else:
                raise RuntimeError(f"Unable to parse [{src}]")
        else:
            raise ValueError(f"Unable to parse [{src}]")

    def __add__(self, other) -> "Frequency":
        if isinstance(other, Frequency):
            return Frequency(self.__freq + other.as_float(self.__unit), self.__unit)
        else:
            raise ValueError(f"Frequency can only be added to another Frequency")

    def __sub__(self, other) -> "Frequency":
        if isinstance(other, Frequency):
            return Frequency(self.__freq - other.as_float(self.__unit), self.__unit)
        else:
            raise ValueError(f"Frequency can only be subtracted from another Frequency")

    def __rtruediv__(self, other) -> "Duration":
        if isinstance(other, int) or isinstance(other, float):
            return Duration(1 / self.as_float(), self.__unit.matching_time_unit())
        else:
            raise ValueError(f"Frequency can only divide a number")

    def __truediv__(self, other) -> "Frequency":
        if isinstance(other, int) or isinstance(other, float):
            return Frequency(self.__freq / other, self.__unit)
        else:
            raise ValueError("Frequency can only be divided by a number")

    def __rmul__(self, other) -> "Frequency":
        if isinstance(other, int) or isinstance(other, float):
            return Frequency(other * self.__freq, self.__unit)
        else:
            raise ValueError("Frequency can only be multiplied by a number")

    def __mul__(self, other) -> "Frequency":
        if isinstance(other, int) or isinstance(other, float):
            return Frequency(self.__freq * other, self.__unit)
        else:
            raise ValueError(f"Frequency can only be multiplied by a number")

    def __lt__(self, other) -> bool:
        if not isinstance(other, Frequency):
            raise TypeError(f"Cannot compare {self} to {other}")
        else:
            return self.__freq < other.as_float(self.__unit)

    def __le__(self, other) -> bool:
        return self == other or self < other

    def __eq__(self, other) -> bool:
        if not isinstance(other, Frequency):
            return False
        elif self.__unit == other.__unit:
            return self.__freq == other.__freq
        else:
            return self.__freq == other.as_float(self.__unit)

    def __repr__(self):
        return f"{self.__freq} {self.__unit.value}"

    def as_float(self, unit: FrequencyUnit | str | None = None) -> float:
        if unit is None:
            return self.__freq
        else:
            return self.__freq * FrequencyUnit.value_of(unit).period_in_seconds() / self.__unit.period_in_seconds()

    def in_unit(self, unit: str | FrequencyUnit) -> "Frequency":
        return Frequency(self.as_float(unit), FrequencyUnit.value_of(unit))

    @property
    def unit(self) -> FrequencyUnit:
        return self.__unit


class TimeUnit(Enum):
    s = "s"
    ms = "ms"
    us = "us"
    ns = "ns"
    ps = "ps"

    def as_seconds(self) -> float:
        match self:
            case TimeUnit.s:
                return 1
            case TimeUnit.ms:
                return 1e-3
            case TimeUnit.us:
                return 1e-6
            case TimeUnit.ns:
                return 1e-9
            case TimeUnit.ps:
                return 1e-12
            case _:
                raise RuntimeError("Invalid time unit")

    @staticmethod
    def value_of(src: Any) -> "TimeUnit":
        if isinstance(src, TimeUnit):
            return src
        elif isinstance(src, str):
            match src.strip().lower():
                case "s":
                    return TimeUnit.s
                case "ms":
                    return TimeUnit.ms
                case "us":
                    return TimeUnit.us
                case "ns":
                    return TimeUnit.ns
                case "ps":
                    return TimeUnit.ps
                case _:
                    raise RuntimeError("Invalid time unit")
        else:
            raise RuntimeError("Invalid time unit")

    def matching_frequency_unit(self) -> "FrequencyUnit":
        match self:
            case TimeUnit.s:
                return FrequencyUnit.Hz
            case TimeUnit.ms:
                return FrequencyUnit.KHz
            case TimeUnit.us:
                return FrequencyUnit.MHz
            case TimeUnit.ns:
                return FrequencyUnit.GHz
            case TimeUnit.ps:
                return FrequencyUnit.THz


class Duration:
    def __init__(self, value: float, time_unit: TimeUnit):
        self.__value = value
        self.__unit = time_unit

    def __repr__(self):
        return f"{self.__value} {self.__unit.value}"

    @staticmethod
    def value_of(src: Any) -> "Duration":
        if isinstance(src, Duration):
            return src
        elif isinstance(src, str):
            src_clean = src.strip().lower()
            if src_clean.endswith("ps"):
                return Duration(float(src_clean.replace("ps", "")), TimeUnit.ps)
            elif src_clean.endswith("ns"):
                return Duration(float(src_clean.replace("ns", "")), TimeUnit.ns)
            elif src_clean.endswith("us"):
                return Duration(float(src_clean.replace("us", "")), TimeUnit.us)
            elif src_clean.endswith("ms"):
                return Duration(float(src_clean.replace("ms", "")), TimeUnit.ms)
            elif src_clean.endswith("s"):
                return Duration(float(src_clean.replace("s", "")), TimeUnit.s)
            else:
                raise RuntimeError(f"Invalid duration [{src}]")
        else:
            raise RuntimeError(f"Invalid duration [{src}]")

    def in_unit(self, unit: str | TimeUnit) -> "Duration":
        return Duration(self.as_float(unit), TimeUnit.value_of(unit))

    def as_float(self, unit: str | TimeUnit | None = None) -> float:
        if unit is None:
            return self.__value
        else:
            return self.__value * self.__unit.as_seconds() / TimeUnit.value_of(unit).as_seconds()

    def __add__(self, other) -> "Duration":
        if isinstance(other, Duration):
            return Duration(self.__value + other.as_float(self.__unit), self.__unit)
        else:
            raise ValueError(f"Duration can only be added to another Duration")

    def __sub__(self, other) -> "Duration":
        if isinstance(other, Duration):
            return Duration(self.__value - other.as_float(self.__unit), self.__unit)
        else:
            raise ValueError(f"Duration can only be subtracted from another Duration")

    def __rtruediv__(self, other) -> "Frequency":
        if isinstance(other, int) or isinstance(other, float):
            return Frequency(1 / self.as_float(), self.__unit.matching_frequency_unit())
        else:
            raise ValueError(f"Duration can only divide a number")

    def __truediv__(self, other) -> "Duration":
        if isinstance(other, int) or isinstance(other, float):
            return Duration(self.__value / other, self.__unit)
        else:
            raise ValueError("Duration can only be divided by a number")

    def __rmul__(self, other) -> "Duration":
        if isinstance(other, int) or isinstance(other, float):
            return Duration(other * self.__value, self.__unit)
        else:
            raise ValueError("Duration can only be multiplied by a number")

    def __mul__(self, other) -> "Duration":
        if isinstance(other, int) or isinstance(other, float):
            return Duration(self.__value * other, self.__unit)
        else:
            raise ValueError(f"Duration can only be multiplied by a number")

    def __lt__(self, other) -> bool:
        if not isinstance(other, Duration):
            raise TypeError(f"Cannot compare {self} to {other}")
        else:
            return self.__value < other.as_float(self.__unit)

    def __le__(self, other) -> bool:
        return self == other or self < other

    def __eq__(self, other) -> bool:
        if not isinstance(other, Duration):
            return False
        elif self.__unit == other.__unit:
            return self.__value == other.__value
        else:
            return self.__value == other.as_float(self.__unit)

    @property
    def unit(self) -> TimeUnit:
        return self.__unit


def F(src: str | Frequency) -> Frequency:
    return Frequency.value_of(src)


def dt(src: str | Duration) -> Duration:
    return Duration.value_of(src)
