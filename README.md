# _Trace Tool_ - ChipScope trace viewer and annotator.

## Introduction

[ChipScope](https://www.xilinx.com/products/intellectual-property/chipscope_ila.html) is an IP core provided
by Xilinx/AMD for many of their series FPGA chips. When installed it can capture analog and digital signals for any
specific net/wire. In that, conceptually, it is not dissimilar from Oscilloscope. The difference being that it
can provide access to signals inside the chip which are not routed out to chip pads and pins. In the lab it is
commonly triggered through Vivado IDE which produces a csv file with each column holding a trace, column name
being name of trace. While generated file is technically a csv file its interpretation by common tools like Excel
and others is challenging as second row typically contains radix information for each column such as HEX, SIGNED,
UNSIGNED and so on. This is intended for correct interpretation of numerical values in each trace column. Regardless
of that Excel is often use to plot and analyze traces. This is very slow and error-prone. Additionally, Vivado will
normally override the same csv file making it difficult to track history of the traces, i.e. being able to see
how any given trace looked like before and after some change to the Verilog code was applied.

"_Trace Tool_" (TT), is an application that addresses above-mentioned issues and also provides additional
functionality of annotating traces, creating trace views for presentation and analysis, tracking history of any
given trace and so on.

## Installation

Trace Tool is written in python 3.13 and can be installed on Windows, Mac or Linux. Snippets below address Windows
installation.

First you need to ensure that you have installed:

1. [Python 3.13](https://www.python.org/downloads/release/python-3131/)
2. [pipx](https://pipx.pypa.io/stable/)

Once above is complete open PowerShell window and run

```shell
pipx install --python 3.13 git+https://github.com/priimak/tt.git@release
```

This will install latest release of trace tool and make it available as `tt.exe` in PowerShell. You can now run
it from PowerShell by simply typing

```shell
tt
```

If new release of Trace Tool is available you can download it by running in PowerShell

```shell
pipx upgrade tt
```

