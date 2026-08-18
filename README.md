# IDataProject

This repository now includes a small, standard-library Python implementation for evaluating
T2UHF RFID calibration results against barcode scanning performance.

## What it does

The calibration logic checks whether T2UHF RFID scanning:

- meets accuracy and stability targets,
- delivers a measurable range advantage over barcode scanning, and
- avoids becoming excessively slower than barcode scanning.

It also returns a recommended transmit-power adjustment so calibration can be tuned upward
when RFID results are weak and downward when latency is the only problem.

## Files

- `rfid_calibration.py` - calibration logic and report model
- `tests/test_rfid_calibration.py` - focused unit tests

## Example

```python
from rfid_calibration import ScanMetrics, evaluate_t2uhf_calibration

report = evaluate_t2uhf_calibration(
    rfid_metrics=ScanMetrics(range_meters=5.2, accuracy=0.98, latency_ms=80, stability=0.95),
    barcode_metrics=ScanMetrics(range_meters=1.0, accuracy=0.96, latency_ms=70, stability=0.99),
    current_power_dbm=20,
)

print(report.to_dict())
```

## Running tests

```bash
python -m unittest discover -s tests
```
