[<](README.md) [>](USAGE.md)

# Installation

Trace Tool is written in pure python 3.13 and can be installed on Windows, Mac or Linux. Snippets below
address Windows installation.

Open PowerShell window and install [uv](https://docs.astral.sh/uv/) (application for managing python
and python based applications). You can skip this step if `uv` is already installed.

```shell
winget install --id=astral-sh.uv  -e
```

Once `uv` is installed run

```shell
uv tool install --cache-dir .cache -p 3.13.1 --force git+https://github.com/priimak/tt.git@release
```

This will install latest release version of _Trace Tool_.

If newer version of Trace Tool is available then you can upgrade your previously installed version
by running following command in PowerShell window.

```shell
uv tool upgrade tt
```