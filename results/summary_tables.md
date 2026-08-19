
### base=AdamW  meta=?  alpha0=1e-5  noguard
| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |
|---|---|---|---|---|---|---|---|
| ? | plain | 1 | never | never | never | 59.98 | 57.26 |

### base=AdamW  meta=Adam  alpha0=1e-3  guard
| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |
|---|---|---|---|---|---|---|---|
| scalar | plain | 3 | 10.0 | 13.0 | 17.0 | 92.94±0.16 | 92.72±0.14 |
| resnet18_blocks | plain | 3 | 8.3 | 11.7 | 18.7 | 92.19±0.06 | 92.07±0.14 |
| layerwise | plain | 3 | 9.7 | 15.0 | 33.0 | 91.07±0.17 | 90.81±0.26 |

### base=AdamW  meta=Adam  alpha0=1e-4  guard
| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |
|---|---|---|---|---|---|---|---|
| scalar | plain | 3 | 9.0 | 15.0 | 27.3 | 92.29±0.09 | 92.08±0.20 |
| resnet18_blocks | plain | 3 | 9.3 | 16.3 | 29.3 | 92.03±0.18 | 91.38±0.11 |
| layerwise | plain | 3 | 7.7 | 12.7 | 19.3 | 92.25±0.18 | 92.12±0.30 |

### base=AdamW  meta=Adam  alpha0=1e-6  guard
| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |
|---|---|---|---|---|---|---|---|
| scalar | plain | 3 | 10.7 | 19.0 | 32.3 | 92.09±0.06 | 91.67±0.27 |
| resnet18_blocks | plain | 3 | 10.3 | 16.0 | 30.7 | 92.03±0.18 | 91.92±0.16 |
| layerwise | plain | 3 | 10.0 | 15.0 | 27.0 | 91.98±0.12 | 91.83±0.29 |

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

### base=SGDm  meta=Adam  alpha0=1e-3  guard
| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |
|---|---|---|---|---|---|---|---|
| scalar | plain | 1 | 24.0 | 83.0 | never | 88.24 | 88.08 |
| resnet18_blocks | plain | 1 | 14.0 | 18.0 | 30.0 | 91.50 | 91.21 |
| layerwise | plain | 1 | 12.0 | 20.0 | 40.0 | 91.57 | 91.27 |

### base=SGDm  meta=Adam  alpha0=1e-4  guard
| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |
|---|---|---|---|---|---|---|---|
| layerwise | shrink(lam=0.1) | 1 | 14.0 | 14.0 | 17.0 | 92.13 | 91.70 |

### base=SGDm  meta=Adam  alpha0=1e-6  guard
| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |
|---|---|---|---|---|---|---|---|
| scalar | plain | 3 | 50.5 (2/3) | 69.0 (1/3) | never | 65.26±38.43 | 65.10±38.29 |
| resnet18_blocks | plain | 3 | 15.3 | 20.3 | 42.0 | 90.94±0.12 | 90.81±0.15 |
| layerwise | plain | 8 | 15.0 | 27.1 | 61.2 | 90.73±0.12 | 90.42±0.17 |
| layerwise | shrink(lam=0.1) | 5 | 15.2 | 16.2 | 19.4 | 92.28±0.12 | 91.86±0.29 |

### base=SGDm  meta=Adam  alpha0=1e-6  noguard
| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |
|---|---|---|---|---|---|---|---|
| scalar | plain | 3 | 24.0 (1/3) | 55.0 (1/3) | never | 42.54±39.77 | 42.22±39.64 |
| resnet18_blocks | plain | 3 | 15.7 | 20.7 | 47.3 | 90.81±0.07 | 90.62±0.09 |
| layerwise | plain | 3 | 15.3 | 25.3 | 57.3 | 90.79±0.29 | 90.40±0.26 |
| weightwise | plain | 3 | never | never | never | 50.75±0.75 | 50.72±0.75 |

### base=SGDm  meta=Lion  alpha0=1e-3  guard
| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |
|---|---|---|---|---|---|---|---|
| scalar | plain | 5 | 24.2 | 76.2 | never | 88.32±0.15 | 88.08±0.16 |
| resnet18_blocks | plain | 2 | 15.5 | 22.0 | 31.0 | 91.72±0.18 | 91.57±0.21 |
| layerwise | plain | 5 | 13.4 | 23.4 | 41.0 | 91.76±0.25 | 91.58±0.31 |
| layerwise | shrink(lam=0.1) | 5 | 17.6 | 20.2 | 23.4 | 92.52±0.10 | 92.24±0.12 |

### base=SGDm  meta=Lion  alpha0=1e-4  guard
| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |
|---|---|---|---|---|---|---|---|
| scalar | plain | 2 | 26.5 | 66.0 (1/2) | never | 88.19±0.32 | 88.00±0.45 |
| resnet18_blocks | plain | 2 | 20.0 | 27.5 | 34.0 | 91.67±0.16 | 91.47±0.28 |
| layerwise | plain | 2 | 19.5 | 26.5 | 42.0 | 91.41±0.25 | 91.14±0.33 |
| layerwise | shrink(lam=0.1) | 2 | 24.5 | 26.5 | 30.0 | 92.72±0.04 | 92.52±0.06 |

### base=SGDm  meta=Lion  alpha0=1e-6  guard
| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |
|---|---|---|---|---|---|---|---|
| scalar | plain | 5 | 37.0 | 90.3 (3/5) | never | 88.08±0.22 | 87.85±0.18 |
| resnet18_blocks | plain | 5 | 29.4 | 36.6 | 43.8 | 91.69±0.13 | 91.42±0.23 |
| resnet18_blocks | shrink(lam=0.1) | 6 | 31.2 | 39.8 | 53.0 | 92.08±0.15 | 91.77±0.12 |
| layerwise | plain | 11 | 29.0 | 36.2 | 56.5 | 91.23±0.22 | 90.85±0.31 |
| layerwise | shrink(lam=0.001) | 3 | 32.0 | 39.7 | 48.3 | 92.54±0.20 | 92.37±0.13 |
| layerwise | shrink(lam=0.01) | 3 | 36.3 | 37.3 | 41.0 | 92.79±0.11 | 92.75±0.17 |
| layerwise | shrink(lam=0.03) | 2 | 35.5 | 37.5 | 41.0 | 92.56±0.09 | 92.28±0.11 |
| layerwise | shrink(lam=0.1) | 11 | 35.5 | 38.1 | 41.4 | 92.59±0.09 | 92.34±0.22 |
| layerwise | shrink(lam=0.3) | 1 | 36.0 | 38.0 | 42.0 | 92.76 | 92.42 |
| layerwise | shrink(lam=0.5) | 3 | 36.0 | 38.0 | 41.7 | 92.50±0.14 | 92.32±0.16 |
| layerwise | shrink(lam=1.0) | 3 | 35.7 | 38.0 | 41.3 | 92.53±0.17 | 92.36±0.15 |
| weightwise | additive(r=0.1) | 2 | never | never | never | 51.30±2.03 | 51.30±2.03 |
| weightwise | additive(r=0.3) | 2 | never | never | never | 66.61±0.74 | 66.61±0.74 |
| weightwise | plain | 3 | never | never | never | 79.38±0.46 | 79.38±0.46 |
| weightwise | shrink(lam=0.00001) | 2 | never | never | never | 78.98±0.17 | 78.98±0.17 |
| weightwise | shrink(lam=0.0001) | 2 | never | never | never | 70.23±0.15 | 70.23±0.15 |
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

(219 runs with >= 100 epochs, of 255 total)
