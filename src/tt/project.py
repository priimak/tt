import dataclasses
import hashlib
import json
import os.path
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, override

import polars
from polars import DataFrame
from returns.result import Result, Failure, Success


class C2Dict(ABC):
    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        pass

    def to_json_file(self, file: Path) -> Result[None, BaseException]:
        try:
            file.write_text(json.dumps(self.to_dict(), indent = 2))
            return Success(None)
        except BaseException as ex:
            return Failure(ex)


class TraceSource(C2Dict, ABC):
    @abstractmethod
    def load_as_dataframe(self) -> DataFrame:
        pass

    @abstractmethod
    def has_changed(self) -> bool:
        pass

    @abstractmethod
    def update_changed_id(self) -> None:
        pass

    @staticmethod
    def from_csv_file(file: Path | str) -> "TraceSource":
        src = Path(file)
        if src.exists() and src.is_file():
            return CSVFileTraceSource(src)
        else:
            raise RuntimeError(f"File {file} not found")


class TraceSourceFactory:
    @staticmethod
    def from_dict(d: dict[str, Any]) -> Result[TraceSource, BaseException]:
        source_type = d.get("type", "")
        match source_type:
            case "csv_file":
                return CSVFileTraceSourceFactory.from_dict(d)
            case _:
                return Failure(Exception(f"Unknown source type {source_type}"))


class CSVFileTraceSource(TraceSource):
    def __init__(self, file: Path, last_modified: float | None = None):
        self.file = file
        self.mtime = os.path.getmtime(file) if last_modified is None else last_modified

    @override
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "csv_file",
            "path": f"{self.file}",
            "last_modified": self.mtime
        }

    @override
    def __eq__(self, other):
        return isinstance(other, CSVFileTraceSource) and self.file == other.file

    @override
    def load_as_dataframe(self) -> DataFrame:
        return polars.read_csv(self.file)

    @override
    def has_changed(self) -> bool:
        return self.mtime != os.path.getmtime(self.file)

    def update_changed_id(self) -> None:
        self.mtime = os.path.getmtime(self.file)


class CSVFileTraceSourceFactory:
    @staticmethod
    def from_dict(d: dict[str, Any]) -> Result[CSVFileTraceSource, BaseException]:
        try:
            if d.get("type", "") == "csv_file" and "path" in d:
                return Success(CSVFileTraceSource(Path(d.get("path")), d.get("last_modified")))
            else:
                raise Exception(f"Unable to parse {d} as CSVFileTraceSourc")
        except BaseException as ex:
            return Failure(ex)


class TraceState(StrEnum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


@dataclass
class TraceMetadata:
    name: str
    label: str
    description: str
    state: TraceState


@dataclass
class CommonDataMetadata:
    traces: list[TraceMetadata]


class CommonDataMetadataFactory:
    @staticmethod
    def value_of(data_config_file: Path) -> CommonDataMetadata:
        data_config = json.loads(data_config_file.read_text())
        return CommonDataMetadata(**data_config)


# class Traces(Sequence):
#     pass


# @overload
# def __getitem__(self, index: int) -> _T_co: ...


class Project(C2Dict):
    def __init__(self, *, name: str, dir: Path, traces_src: TraceSource, implied_dx: float,
                 latest_traces_version: int) -> None:
        """
        :param name: Name of the project
        :param dir: directory where project is stored
        :param traces_src: source of traces
        :param implied_dx: implied dt (or dx) step on traces if not available in the traces_src
        :param latest_traces_version: version of the latest traces loaded from the
        """
        self.__name = name
        self.dir = dir
        self.data_config_file = self.dir / "data" / "config.json"
        self.traces_src = traces_src
        self._implied_dx = implied_dx
        self.latest_traces_version = latest_traces_version
        self.traces = Project.TraceVersions(self)

    # dir: Path
    # traces_src: TraceSource

    class Traces(Sequence[TraceMetadata]):
        def __init__(self, project: "Project", version: int):
            self.project = project
            data_config = json.loads(project.data_config_file.read_text())
            self.md = CommonDataMetadata(**data_config)

        def __len__(self) -> int:
            return len(self.md.traces)

        def __getitem__(self, name: str) -> TraceMetadata:
            print(f"name = {name}")
            return None

        def __repr__(self):
            return ", ".join([x["name"] for x in self.md.traces])

    class TraceVersions(Sequence[Traces]):
        def __init__(self, project: "Project"):
            self.project = project

        def __len__(self) -> int:
            return self.project.latest_traces_version

        def __getitem__(self, index: int) -> "Project.Traces":
            idx = self.project.latest_traces_version + index if index < 0 else index
            if idx <= 0 or idx > self.project.latest_traces_version:
                raise IndexError(f"index {index} out of range")
            else:
                return Project.Traces(self.project, index)



    def save(self) -> None:
        self.to_json_file(self.dir / "project.json")

    # def traces(self, version: int) -> TraceVersions:
    #     pass

    def load_traces(self) -> Result[bool, BaseException]:
        """
        Loads traces from the source and saves into a internal persistant store
        """
        try:
            if self.latest_traces_version == 0 or self.traces_src.has_changed():
                self.traces_src.update_changed_id()
                df = self.traces_src.load_as_dataframe()
                self.latest_traces_version += 1
                target_dir = self.dir / "data" / f"{self.latest_traces_version:05}"
                target_dir.mkdir(parents = True, exist_ok = True)
                df.write_parquet(file = target_dir / "traces.parquet.lz4", compression = "lz4")

                if self.data_config_file.exists():
                    # confirm that all columns/traces that we knew prior are still there
                    # it is ok if new columns/traces are added though
                    data_config = json.loads(self.data_config_file.read_text())
                    md = CommonDataMetadata(**data_config)
                    col_name_diff = set([c for c in df.columns]) - set([x["name"] for x in md.traces])
                    if col_name_diff != set():
                        raise RuntimeError(f"Following traces {col_name_diff} are not found in source")
                else:
                    # create common metadata config
                    cdm = CommonDataMetadata(
                        traces = [
                            TraceMetadata(name = c, label = c, description = "", state = TraceState.ACTIVE)
                            for c in df.columns
                        ]
                    )
                    self.data_config_file.write_text(json.dumps(dataclasses.asdict(cdm), indent = 2))
                return Success(True)
            else:
                return Success(False)
        except BaseException as ex:
            return Failure(ex)
        finally:
            self.save()

    @property
    def name(self) -> str:
        return self.__name

    def get_implied_dx(self) -> float:
        """ Step on x-axis (most likely time axis and therefore dt) """
        return self._implied_dx

    def set_implied_dx(self, dx: float) -> Result[None, BaseException]:
        self._implied_dx = dx
        return self.to_json_file(self.dir / "project.json")

    def rename(self, value: str) -> Result[None, BaseException]:
        new_project_dir = self.dir.parent / value
        if new_project_dir == self.dir:
            return Success(None)

        elif new_project_dir.exists():
            return Failure(RuntimeError(f"{new_project_dir} already exists"))

        else:
            self.__name = value
            self.dir = self.dir.rename(new_project_dir)
            self.dir.mkdir(parents = True, exist_ok = True)
            return self.to_json_file(self.dir / "project.json")

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_version": 1,
            "name": self.__name,
            "dir": f"{self.dir}",
            "traces_src": self.traces_src.to_dict(),
            "implied_dx": self._implied_dx,
            "latest_traces_version": self.latest_traces_version,
        }

    @override
    def __repr__(self):
        return json.dumps(self.to_dict(), indent = 2)


class ProjectFactory:
    @staticmethod
    def from_json_file(file: Path) -> Result[Project, BaseException]:
        try:
            data = json.loads(file.read_bytes())
            return Success(Project(
                name = data["name"],
                dir = Path(data["dir"]),
                implied_dx = data["implied_dx"],
                traces_src = TraceSourceFactory.from_dict(data["traces_src"]).unwrap(),
                latest_traces_version = data["latest_traces_version"],
            ))
        except BaseException as ex:
            return Failure(ex)


class ProjectManager:
    def __init__(self, projects_dir: Path):
        self.projects_dir = projects_dir

    def list_project_names(self) -> list[str]:
        return [x.parent.__name for x in sorted(self.projects_dir.glob("**/project.json"))]

    def get_project_by_name(self, name: str) -> Result[Project, BaseException]:
        return ProjectFactory.from_json_file(self.projects_dir / name / "project.json")

    def project_from_csv_file(self, csv_file: Path | str) -> Result[Project, BaseException]:
        try:
            project_name = hashlib.sha1(f"{csv_file}".encode()).hexdigest()
            project_dir = self.projects_dir / project_name
            if project_dir.exists():
                return Success(ProjectFactory.from_json_file(project_dir / "project.json").unwrap())
            else:
                csv_tr_src = TraceSource.from_csv_file(csv_file)
                found_projects = [
                    x
                    for p in self.list_project_names()
                    if (x := self.get_project_by_name(p).unwrap()).traces_src == csv_tr_src
                ]
                if len(found_projects) == 1:
                    return Success(found_projects[0])
                elif len(found_projects) > 1:
                    return Failure(Exception(f"Multiple projects found for {project_name}"))
                else:
                    # this is a brand-new project
                    project = Project(
                        name = project_name,
                        dir = project_dir,
                        traces_src = TraceSource.from_csv_file(csv_file),
                        implied_dx = 1,
                        latest_traces_version = 0
                    )
                    project_dir.mkdir(parents = True, exist_ok = True)
                    project.to_json_file(project_dir / "project.json")

                    # since this is a brand-new project we will load content of the csv file and record it as version 1.
                    return project.load_traces().map(lambda _: project)
        except BaseException as ex:
            return Failure(ex)


if __name__ == '__main__':
    pm = ProjectManager(Path.home() / ".tt" / "projects")
    # names = pm.list_project_names()
    # print(names)
    project: Result[Project, BaseException] = pm.project_from_csv_file(Path.home() / "Downloads" / "iladata.csv")
    print(project)
    p = project.unwrap()
    p.load_traces()
    print(p.traces[-1])
    # print(project)
    # load_results = project.unwrap().load_traces()
    # print(load_results)

    # x = project.bind(lambda x: x.rename("rrr"))
    # unwrap: Project = project.unwrap()
    # x = unwrap.name()
    # unwrap.name("foobar")
    # print(project.bind(lambda x: x.get_implied_dx()))
    # print(pm.get_project_by_name("rrr"))
    # unwrap: Project = project.unwrap()
    # print(unwrap)
    # print(unwrap.rename("foobar"))
