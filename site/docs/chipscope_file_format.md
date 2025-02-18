# Chipscope csv file format

Chipscope generated csv file has a specific structure that look like so

```text
Sample in Buffer,Sample in Window,TRIGGER,aCore/Gen/foo[15:0],aCore/Gen/xyz[15:0]
Radix - UNSIGNED,UNSIGNED,UNSIGNED,SIGNED,SIGNED
0,0,0,83,39417
1,1,0,96,394A4
2,2,0,102,39410
...
```

Or better formatted:

| Sample in Buffer | Sample in Window | TRIGGER  | aCore/Gen/foo[15:0] | aCore/Gen/xyz[15:0] |
|------------------|------------------|----------|---------------------|---------------------|
| Radix - UNSIGNED | UNSIGNED         | UNSIGNED | SIGNED              | HEX                 |
| 0                | 0                | 0        | 83                  | 39417               |
| 1                | 1                | 0        | 96                  | 394A7               |
| 2                | 2                | 0        | 102                 | 39410               |

First row contains column names which are trace names. Second row contains radix for subsequent numeric values.
Starting from the third row is actual trace data.