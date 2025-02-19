Trace Tool
===========

_Version: 0.11.0_

[ChipScope](https://www.xilinx.com/products/intellectual-property/chipscope_ila.html) is an IP core provided
by Xilinx/AMD for many of their series FPGA chips. When installed it can capture analog and digital signals for any
specific net/wire. In that, conceptually, it is not dissimilar from Oscilloscope. The difference being that it
can provide access to signals inside the chip which are not routed out to chip pads and pins. In the lab it is
commonly triggered through Vivado IDE which produces a csv file with each column holding a trace, column name
being name of trace. While generated file is technically a csv file its interpretation by common tools like Excel
and others is challenging as second row typically contains radix information for each column such as HEX, SIGNED,
UNSIGNED and so on. This is intended for correct interpretation of numerical values in each trace column. Regardless
of that, Excel is often use to plot and analyze traces. This is very slow and error-prone. Additionally, Vivado will
normally override the same csv file making it difficult to track history of the traces, i.e. being able to see
how any given trace looked like before and after some change to the Verilog code was applied.

"_Trace Tool_" (TT), is an application that addresses above-mentioned issues and also provides additional
functionality for annotating traces, creating trace views for presentation and analysis, tracking history of any
given trace and many more.
