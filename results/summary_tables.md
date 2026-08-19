
### base=AdamW  meta=?  alpha0=1e-5  noguard
| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |
|---|---|---|---|---|---|---|---|
| ? | plain | 1 | never | never | never | 59.98 | 57.26 |

### base=AdamW  meta=Adam  alpha0=1e-6  noguard
| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |
|---|---|---|---|---|---|---|---|
| scalar | plain | 3 | 10.7 | 19.0 | 30.7 | 91.93±0.26 | 91.76±0.21 |
| resnet18_blocks | plain | 3 | 10.0 | 16.0 | 27.3 | 92.06±0.12 | 91.83±0.12 |
| layerwise | plain | 3 | 8.7 | 15.3 | 25.0 | 92.09±0.10 | 91.73±0.25 |

### base=AdamW  meta=Lion  alpha0=1e-6  noguard
| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |
|---|---|---|---|---|---|---|---|
| scalar | plain | 3 | 13.0 | 20.3 | 33.3 | 91.99±0.10 | 91.50±0.47 |
| resnet18_blocks | plain | 3 | 13.0 | 17.7 | 35.7 | 91.86±0.30 | 91.35±0.31 |
| layerwise | plain | 3 | 13.3 | 17.7 | 32.7 | 91.83±0.17 | 91.58±0.37 |
| weightwise | plain | 3 | 64.3 | never | never | 86.05±0.29 | 85.51±0.54 |

### base=HF  meta=?  alpha0=1e-6  noguard
| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |
|---|---|---|---|---|---|---|---|
| scalar | plain | 7 | 12.7 (3/7) | 18.3 (3/7) | 30.7 (3/7) | 80.05±11.67 | 79.66±11.64 |
| resnet18_blocks | plain | 7 | 11.7 (3/7) | 17.7 (3/7) | 30.7 (3/7) | 78.54±12.82 | 78.09±12.75 |

### base=SGDm  meta=Adam  alpha0=1e-6  noguard
| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |
|---|---|---|---|---|---|---|---|
| scalar | plain | 3 | 24.0 (1/3) | 55.0 (1/3) | never | 42.54±39.77 | 42.22±39.64 |
| resnet18_blocks | plain | 3 | 15.7 | 20.7 | 47.3 | 90.81±0.07 | 90.62±0.09 |
| layerwise | plain | 3 | 15.3 | 25.3 | 57.3 | 90.79±0.29 | 90.40±0.26 |
| weightwise | plain | 3 | never | never | never | 50.75±0.75 | 50.72±0.75 |

### base=SGDm  meta=Lion  alpha0=1e-6  guard
| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |
|---|---|---|---|---|---|---|---|
| layerwise | plain | 3 | 28.7 | 36.0 | 54.7 | 91.39±0.19 | 90.98±0.42 |
| layerwise | shrink(lam=0.1) | 2 | 35.5 | 38.0 | 41.5 | 92.53±0.04 | 92.31±0.22 |
| weightwise | additive(r=0.1) | 1 | never | never | never | 49.87 | 49.87 |
| weightwise | additive(r=0.3) | 1 | never | never | never | 67.13 | 67.13 |
| weightwise | plain | 3 | never | never | never | 79.38±0.46 | 79.38±0.46 |
| weightwise | shrink(lam=0.01) | 2 | never | never | never | 49.73±3.51 | 49.73±3.51 |
| weightwise | shrink(lam=0.1) | 2 | never | never | never | 49.07±3.75 | 49.07±3.75 |
| weightwise | shrink(lam=0.5) | 2 | never | never | never | 49.06±3.80 | 49.06±3.80 |

### base=SGDm  meta=Lion  alpha0=1e-6  noguard
| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |
|---|---|---|---|---|---|---|---|
| scalar | plain | 6 | 37.3 | 90.2 (4/6) | never | 88.07±0.12 | 87.95±0.14 |
| resnet18_blocks | plain | 6 | 30.0 | 36.0 | 43.5 | 91.55±0.13 | 91.40±0.20 |
| layerwise | plain | 4 | 28.2 | 36.0 | 54.2 | 91.31±0.09 | 91.06±0.10 |
| weightwise | plain | 10 | never | never | never | 67.23±3.40 | 10.00±0.00 |

(90 runs with >= 100 epochs, of 118 total)
