
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
| scalar | plain | 2 | 25.0 | 83.0 (1/2) | never | 88.06±0.25 | 87.88±0.28 |
| resnet18_blocks | plain | 2 | 14.5 | 19.0 | 30.0 | 91.36±0.20 | 91.07±0.19 |
| layerwise | plain | 2 | 12.0 | 20.0 | 38.0 | 91.60±0.04 | 91.41±0.19 |
| layerwise | shrink(lam=0.1) | 1 | 13.0 | 14.0 | 17.0 | 92.17 | 92.17 |

### base=SGDm  meta=Adam  alpha0=1e-4  guard
| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |
|---|---|---|---|---|---|---|---|
| scalar | plain | 1 | 24.0 | 94.0 | never | 88.15 | 88.15 |
| resnet18_blocks | plain | 1 | 13.0 | 19.0 | 29.0 | 91.42 | 91.22 |
| layerwise | plain | 1 | 13.0 | 20.0 | 40.0 | 91.38 | 90.91 |
| layerwise | shrink(lam=0.1) | 2 | 13.5 | 14.0 | 18.5 | 92.12±0.01 | 91.57±0.18 |

### base=SGDm  meta=Adam  alpha0=1e-6  guard
| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |
|---|---|---|---|---|---|---|---|
| scalar | plain | 4 | 41.7 (3/4) | 68.5 (2/4) | never | 71.06±33.46 | 70.83±33.30 |
| resnet18_blocks | plain | 4 | 15.2 | 20.2 | 39.2 | 91.03±0.20 | 90.84±0.13 |
| layerwise | additive(r=0.03) | 3 | 17.0 | 24.0 | 33.0 | 91.71±0.07 | 91.38±0.17 |
| layerwise | additive(r=0.1) | 3 | 15.3 | 28.3 | 48.7 | 91.36±0.09 | 91.17±0.31 |
| layerwise | plain | 9 | 15.0 | 26.7 | 59.7 | 90.76±0.14 | 90.47±0.21 |
| layerwise | shrink(lam=0.1) | 6 | 15.2 | 16.0 | 19.3 | 92.30±0.11 | 91.87±0.26 |

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
| scalar | plain | 5 | 24.2 | 76.2 | never | 88.33±0.15 | 88.11±0.21 |
| resnet18_blocks | plain | 2 | 15.5 | 22.0 | 31.0 | 91.72±0.18 | 91.57±0.21 |
| layerwise | plain | 5 | 13.4 | 23.4 | 41.0 | 91.76±0.25 | 91.62±0.33 |
| layerwise | shrink(lam=0.1) | 5 | 17.6 | 20.2 | 23.4 | 92.52±0.10 | 92.12±0.25 |

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
| resnet18_blocks | additive(r=0.03) | 3 | 31.0 | 39.3 | 50.0 | 92.18±0.21 | 92.03±0.22 |
| resnet18_blocks | additive(r=0.1) | 3 | 31.0 | 40.0 | 48.0 | 91.94±0.06 | 91.71±0.32 |
| resnet18_blocks | plain | 5 | 29.4 | 36.6 | 43.8 | 91.69±0.13 | 91.42±0.23 |
| resnet18_blocks | shrink(lam=0.1) | 6 | 31.2 | 39.8 | 53.0 | 92.08±0.15 | 91.77±0.12 |
| resnet18_blocks | shrink(lam=1.0) | 2 | 30.5 | 39.0 | 49.0 | 92.14±0.01 | 91.62±0.12 |
| layerwise | additive(r=0) | 5 | 35.8 | 37.8 | 41.4 | 92.58±0.16 | 92.24±0.30 |
| layerwise | additive(r=0.03) | 5 | 36.4 | 39.0 | 40.6 | 92.96±0.15 | 92.59±0.15 |
| layerwise | additive(r=0.05) | 7 | 36.0 | 39.1 | 41.6 | 93.46±0.05 | 92.98±0.13 |
| layerwise | additive(r=0.07) | 5 | 34.6 | 38.8 | 41.4 | 93.48±0.16 | 93.27±0.17 |
| layerwise | additive(r=0.1) | 7 | 32.6 | 37.4 | 40.7 | 93.04±0.36 | 92.80±0.40 |
| layerwise | additive(r=0.2) | 3 | 31.3 | 35.7 | 43.3 | 91.73±0.15 | 91.53±0.29 |
| layerwise | additive(r=0.3) | 3 | 30.3 | 36.0 | 53.0 | 91.40±0.09 | 91.30±0.05 |
| layerwise | plain | 13 | 29.0 | 36.2 | 56.3 | 91.35±0.36 | 90.98±0.43 |
| layerwise | shrink(lam=0.00001) | 2 | 29.0 | 36.0 | 53.5 | 91.37±0.06 | 91.06±0.39 |
| layerwise | shrink(lam=0.00003) | 2 | 28.5 | 36.5 | 56.5 | 91.30±0.02 | 91.02±0.07 |
| layerwise | shrink(lam=0.0001) | 2 | 29.5 | 36.0 | 61.5 | 91.03±0.06 | 90.75±0.35 |
| layerwise | shrink(lam=0.001) | 3 | 32.0 | 39.7 | 48.3 | 92.54±0.20 | 92.37±0.13 |
| layerwise | shrink(lam=0.01) | 3 | 36.3 | 37.3 | 41.0 | 92.79±0.11 | 92.75±0.17 |
| layerwise | shrink(lam=0.03) | 3 | 36.0 | 37.7 | 41.0 | 92.58±0.08 | 92.34±0.14 |
| layerwise | shrink(lam=0.1) | 14 | 35.6 | 38.0 | 41.4 | 92.58±0.11 | 92.28±0.24 |
| layerwise | shrink(lam=0.3) | 3 | 35.7 | 37.7 | 41.3 | 92.51±0.23 | 92.30±0.12 |
| layerwise | shrink(lam=0.5) | 3 | 36.0 | 38.0 | 41.7 | 92.50±0.14 | 92.32±0.16 |
| layerwise | shrink(lam=1.0) | 3 | 35.7 | 38.0 | 41.3 | 92.53±0.17 | 92.36±0.15 |
| layerwise | zpool(r=0) | 4 | 37.5 | 92.3 (3/4) | never | 88.05±0.20 | 87.90±0.33 |
| layerwise | zpool(r=0.1) | 4 | 33.0 | 52.2 | 98.0 (2/4) | 90.03±0.18 | 89.84±0.30 |
| layerwise | zpool(r=0.3) | 4 | 32.8 | 49.0 | 92.0 (1/4) | 89.99±0.25 | 89.75±0.29 |
| layerwise | zpool(r=0.5) | 4 | 32.5 | 50.0 | never | 89.62±0.11 | 89.38±0.27 |
| layerwise | zpool(r=0.7) | 4 | 32.2 | 52.0 | never | 89.48±0.19 | 88.99±0.16 |
| layerwise | zpool(r=1) | 3 | 28.7 | 36.3 | 56.0 | 91.35±0.16 | 91.12±0.15 |
| nodewise | plain | 4 | 30.5 | 36.8 | 47.8 | 91.89±0.21 | 91.73±0.24 |
| nodewise | shrink(lam=1.0) | 2 | 49.5 | 58.5 | 68.5 | 92.61±0.13 | 92.28±0.20 |
| weightwise | additive(r=0.1) | 2 | never | never | never | 51.30±2.03 | 51.30±2.03 |
| weightwise | additive(r=0.3) | 2 | never | never | never | 66.61±0.74 | 66.61±0.74 |
| weightwise | plain | 3 | never | never | never | 79.38±0.46 | 79.38±0.46 |
| weightwise | shrink(lam=0.00001) | 2 | never | never | never | 78.98±0.17 | 78.98±0.17 |
| weightwise | shrink(lam=0.0001) | 2 | never | never | never | 70.23±0.15 | 70.23±0.15 |
| weightwise | shrink(lam=0.01) | 2 | never | never | never | 49.73±3.51 | 49.73±3.51 |
| weightwise | shrink(lam=0.1) | 2 | never | never | never | 49.07±3.75 | 49.07±3.75 |
| weightwise | shrink(lam=0.5) | 2 | never | never | never | 49.06±3.80 | 49.06±3.80 |
| weightwise | shrink(lam=1.0) | 2 | never | never | never | 48.92±3.83 | 48.92±3.83 |
| weightwise | zpool(r=0) | 4 | 37.5 | 93.2 | never | 88.06±0.03 | 87.95±0.05 |
| weightwise | zpool(r=0.1) | 4 | 37.5 | 86.7 (3/4) | never | 88.20±0.16 | 87.94±0.13 |
| weightwise | zpool(r=0.3) | 4 | 37.8 | 87.5 | never | 88.22±0.18 | 88.05±0.09 |
| weightwise | zpool(r=0.5) | 4 | 37.5 | 88.2 | never | 88.26±0.09 | 88.01±0.30 |
| weightwise | zpool(r=0.7) | 4 | 36.8 | 80.2 | never | 88.50±0.17 | 88.18±0.13 |
| weightwise | zpool(r=1) | 3 | never | never | never | 79.35±0.37 | 79.32±0.37 |

### base=SGDm  meta=Lion  alpha0=1e-6  noguard
| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |
|---|---|---|---|---|---|---|---|
| scalar | plain | 6 | 37.3 | 90.2 (4/6) | never | 88.07±0.12 | 87.95±0.14 |
| resnet18_blocks | plain | 6 | 30.0 | 36.0 | 43.5 | 91.55±0.13 | 91.40±0.20 |
| layerwise | plain | 4 | 28.2 | 36.0 | 54.2 | 91.31±0.09 | 91.06±0.10 |
| weightwise | plain | 10 | never | never | never | 67.23±3.40 | 10.00±0.00 |

(348 runs with >= 100 epochs, of 413 total)
