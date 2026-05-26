# High-D Useful Volume Census

Schema: `monogate.high_dim_useful_volume_census.v1`
Samples per case: `1000`
Tolerance: `0.1`

| depth | distribution | target | finite | non-saturated | target-adjacent | best abs error |
|---:|---|---|---:|---:|---:|---:|
| 1 | raw_cube | zero | 0.470 | 0.470 | 0.0000 | 3.860e-01 |
| 1 | raw_cube | one | 0.489 | 0.488 | 0.0370 | 1.167e-02 |
| 1 | raw_cube | sqrt2 | 0.533 | 0.533 | 0.0370 | 7.589e-03 |
| 1 | raw_cube | e | 0.506 | 0.506 | 0.0230 | 1.560e-03 |
| 1 | raw_cube | pi | 0.528 | 0.528 | 0.0160 | 3.395e-03 |
| 1 | positive_box | zero | 1.000 | 1.000 | 0.0000 | 4.527e-01 |
| 1 | positive_box | one | 1.000 | 1.000 | 0.0310 | 4.547e-03 |
| 1 | positive_box | sqrt2 | 1.000 | 1.000 | 0.0310 | 8.157e-03 |
| 1 | positive_box | e | 1.000 | 1.000 | 0.0400 | 7.376e-04 |
| 1 | positive_box | pi | 1.000 | 1.000 | 0.0340 | 1.426e-03 |
| 1 | guarded_cube | zero | 1.000 | 0.496 | 0.0000 | 3.998e-01 |
| 1 | guarded_cube | one | 1.000 | 0.510 | 0.0340 | 1.346e-02 |
| 1 | guarded_cube | sqrt2 | 1.000 | 0.495 | 0.0340 | 1.829e-03 |
| 1 | guarded_cube | e | 1.000 | 0.520 | 0.0260 | 1.879e-03 |
| 1 | guarded_cube | pi | 1.000 | 0.461 | 0.0190 | 9.274e-03 |
| 2 | raw_cube | zero | 0.234 | 0.152 | 0.0000 | 4.472e-01 |
| 2 | raw_cube | one | 0.251 | 0.147 | 0.0040 | 4.042e-02 |
| 2 | raw_cube | sqrt2 | 0.258 | 0.151 | 0.0040 | 2.303e-02 |
| 2 | raw_cube | e | 0.259 | 0.160 | 0.0040 | 1.307e-03 |
| 2 | raw_cube | pi | 0.239 | 0.151 | 0.0080 | 9.533e-03 |
| 2 | positive_box | zero | 1.000 | 0.380 | 0.0040 | 5.346e-03 |
| 2 | positive_box | one | 1.000 | 0.349 | 0.0140 | 4.485e-03 |
| 2 | positive_box | sqrt2 | 1.000 | 0.354 | 0.0120 | 6.087e-03 |
| 2 | positive_box | e | 1.000 | 0.367 | 0.0100 | 1.092e-02 |
| 2 | positive_box | pi | 1.000 | 0.396 | 0.0130 | 1.515e-02 |
| 2 | guarded_cube | zero | 1.000 | 0.337 | 0.0090 | 3.592e-03 |
| 2 | guarded_cube | one | 1.000 | 0.318 | 0.0060 | 2.071e-02 |
| 2 | guarded_cube | sqrt2 | 1.000 | 0.320 | 0.0110 | 6.630e-03 |
| 2 | guarded_cube | e | 1.000 | 0.331 | 0.0100 | 2.526e-03 |
| 2 | guarded_cube | pi | 1.000 | 0.300 | 0.0050 | 4.433e-03 |
| 3 | raw_cube | zero | 0.080 | 0.019 | 0.0000 | 5.862e-01 |
| 3 | raw_cube | one | 0.061 | 0.013 | 0.0000 | 6.877e-01 |
| 3 | raw_cube | sqrt2 | 0.064 | 0.014 | 0.0000 | 7.623e-01 |
| 3 | raw_cube | e | 0.056 | 0.012 | 0.0000 | 1.207e-01 |
| 3 | raw_cube | pi | 0.079 | 0.019 | 0.0010 | 1.637e-02 |
| 3 | positive_box | zero | 0.905 | 0.131 | 0.0010 | 8.587e-02 |
| 3 | positive_box | one | 0.928 | 0.109 | 0.0020 | 3.520e-02 |
| 3 | positive_box | sqrt2 | 0.920 | 0.112 | 0.0020 | 1.716e-02 |
| 3 | positive_box | e | 0.910 | 0.115 | 0.0010 | 5.355e-03 |
| 3 | positive_box | pi | 0.925 | 0.107 | 0.0020 | 3.555e-03 |
| 3 | guarded_cube | zero | 1.000 | 0.100 | 0.0030 | 3.259e-02 |
| 3 | guarded_cube | one | 1.000 | 0.090 | 0.0010 | 7.737e-02 |
| 3 | guarded_cube | sqrt2 | 1.000 | 0.084 | 0.0010 | 2.974e-02 |
| 3 | guarded_cube | e | 1.000 | 0.078 | 0.0000 | 1.114e-01 |
| 3 | guarded_cube | pi | 1.000 | 0.081 | 0.0010 | 7.372e-02 |
| 4 | raw_cube | zero | 0.003 | 0.002 | 0.0000 | 3.472e+00 |
| 4 | raw_cube | one | 0.005 | 0.000 | 0.0000 | 4.382e+05 |
| 4 | raw_cube | sqrt2 | 0.002 | 0.000 | 0.0000 | 2.039e+01 |
| 4 | raw_cube | e | 0.000 | 0.000 | 0.0000 | n/a |
| 4 | raw_cube | pi | 0.002 | 0.001 | 0.0000 | 2.760e+00 |
| 4 | positive_box | zero | 0.243 | 0.022 | 0.0000 | 4.194e-01 |
| 4 | positive_box | one | 0.248 | 0.016 | 0.0000 | 1.668e-01 |
| 4 | positive_box | sqrt2 | 0.239 | 0.034 | 0.0000 | 3.894e-01 |
| 4 | positive_box | e | 0.248 | 0.021 | 0.0000 | 3.132e-01 |
| 4 | positive_box | pi | 0.252 | 0.028 | 0.0010 | 4.412e-02 |
| 4 | guarded_cube | zero | 1.000 | 0.032 | 0.0010 | 2.669e-02 |
| 4 | guarded_cube | one | 1.000 | 0.042 | 0.0010 | 6.035e-02 |
| 4 | guarded_cube | sqrt2 | 1.000 | 0.036 | 0.0000 | 3.031e-01 |
| 4 | guarded_cube | e | 1.000 | 0.029 | 0.0000 | 6.207e-01 |
| 4 | guarded_cube | pi | 1.000 | 0.039 | 0.0000 | 1.444e+00 |
| 5 | raw_cube | zero | 0.000 | 0.000 | 0.0000 | n/a |
| 5 | raw_cube | one | 0.000 | 0.000 | 0.0000 | n/a |
| 5 | raw_cube | sqrt2 | 0.000 | 0.000 | 0.0000 | n/a |
| 5 | raw_cube | e | 0.000 | 0.000 | 0.0000 | n/a |
| 5 | raw_cube | pi | 0.000 | 0.000 | 0.0000 | n/a |
| 5 | positive_box | zero | 0.016 | 0.000 | 0.0000 | 1.243e+01 |
| 5 | positive_box | one | 0.016 | 0.001 | 0.0000 | 7.399e+00 |
| 5 | positive_box | sqrt2 | 0.020 | 0.004 | 0.0000 | 3.657e+00 |
| 5 | positive_box | e | 0.023 | 0.000 | 0.0000 | 1.991e+01 |
| 5 | positive_box | pi | 0.013 | 0.001 | 0.0000 | 6.402e+00 |
| 5 | guarded_cube | zero | 1.000 | 0.003 | 0.0000 | 3.166e+00 |
| 5 | guarded_cube | one | 1.000 | 0.005 | 0.0000 | 1.959e+00 |
| 5 | guarded_cube | sqrt2 | 1.000 | 0.004 | 0.0000 | 4.445e+00 |
| 5 | guarded_cube | e | 1.000 | 0.008 | 0.0000 | 2.762e+00 |
| 5 | guarded_cube | pi | 1.000 | 0.010 | 0.0000 | 5.604e+00 |
| 6 | raw_cube | zero | 0.000 | 0.000 | 0.0000 | n/a |
| 6 | raw_cube | one | 0.000 | 0.000 | 0.0000 | n/a |
| 6 | raw_cube | sqrt2 | 0.000 | 0.000 | 0.0000 | n/a |
| 6 | raw_cube | e | 0.000 | 0.000 | 0.0000 | n/a |
| 6 | raw_cube | pi | 0.000 | 0.000 | 0.0000 | n/a |
| 6 | positive_box | zero | 0.000 | 0.000 | 0.0000 | n/a |
| 6 | positive_box | one | 0.000 | 0.000 | 0.0000 | n/a |
| 6 | positive_box | sqrt2 | 0.000 | 0.000 | 0.0000 | n/a |
| 6 | positive_box | e | 0.000 | 0.000 | 0.0000 | n/a |
| 6 | positive_box | pi | 0.000 | 0.000 | 0.0000 | n/a |
| 6 | guarded_cube | zero | 1.000 | 0.003 | 0.0000 | 3.031e+00 |
| 6 | guarded_cube | one | 1.000 | 0.001 | 0.0000 | 4.031e+00 |
| 6 | guarded_cube | sqrt2 | 1.000 | 0.004 | 0.0000 | 4.445e+00 |
| 6 | guarded_cube | e | 1.000 | 0.000 | 0.0000 | 1.800e+01 |
| 6 | guarded_cube | pi | 1.000 | 0.003 | 0.0000 | 6.173e+00 |

Target-adjacent volume is sampled evidence only. It is a useful frontier
signal for Forge heuristics, not a proof of symbolic reachability.
