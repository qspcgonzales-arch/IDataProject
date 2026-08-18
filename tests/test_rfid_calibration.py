import unittest

from rfid_calibration import CalibrationSettings, ScanMetrics, evaluate_t2uhf_calibration


class EvaluateT2UhfCalibrationTests(unittest.TestCase):
    def test_successful_calibration_beats_barcode(self) -> None:
        report = evaluate_t2uhf_calibration(
            rfid_metrics=ScanMetrics(range_meters=5.2, accuracy=0.98, latency_ms=80, stability=0.95),
            barcode_metrics=ScanMetrics(range_meters=1.0, accuracy=0.96, latency_ms=70, stability=0.99),
            current_power_dbm=20,
        )

        self.assertTrue(report.beats_barcode)
        self.assertTrue(report.meets_targets)
        self.assertEqual(report.recommended_power_dbm, 20)
        self.assertEqual(report.issues, [])

    def test_low_range_and_accuracy_increase_power(self) -> None:
        report = evaluate_t2uhf_calibration(
            rfid_metrics=ScanMetrics(range_meters=1.1, accuracy=0.9, latency_ms=85, stability=0.88),
            barcode_metrics=ScanMetrics(range_meters=1.0, accuracy=0.92, latency_ms=70, stability=0.99),
            current_power_dbm=20,
        )

        self.assertFalse(report.meets_targets)
        self.assertEqual(report.recommended_power_dbm, 21)
        self.assertIn("RFID accuracy is below target", report.issues)
        self.assertIn("RFID stability is below target", report.issues)
        self.assertIn(
            "RFID range does not exceed barcode range by the required margin",
            report.issues,
        )

    def test_latency_issue_reduces_power_when_other_targets_are_met(self) -> None:
        report = evaluate_t2uhf_calibration(
            rfid_metrics=ScanMetrics(range_meters=2.0, accuracy=0.97, latency_ms=200, stability=0.93),
            barcode_metrics=ScanMetrics(range_meters=1.0, accuracy=0.95, latency_ms=100, stability=0.99),
            current_power_dbm=10,
        )

        self.assertFalse(report.meets_targets)
        self.assertEqual(report.recommended_power_dbm, 9)
        self.assertEqual(report.issues, ["RFID latency is too high compared with barcode scanning"])

    def test_invalid_metrics_raise_value_error(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_t2uhf_calibration(
                rfid_metrics=ScanMetrics(range_meters=-1, accuracy=0.98, latency_ms=80, stability=0.95),
                barcode_metrics=ScanMetrics(range_meters=1.0, accuracy=0.96, latency_ms=70, stability=0.99),
                current_power_dbm=20,
            )

    def test_current_power_is_clamped_to_limits(self) -> None:
        settings = CalibrationSettings(min_power_dbm=5, max_power_dbm=30, power_step_dbm=2)
        report = evaluate_t2uhf_calibration(
            rfid_metrics=ScanMetrics(range_meters=1.1, accuracy=0.9, latency_ms=85, stability=0.88),
            barcode_metrics=ScanMetrics(range_meters=1.0, accuracy=0.92, latency_ms=70, stability=0.99),
            current_power_dbm=40,
            settings=settings,
        )

        self.assertEqual(report.current_power_dbm, 30)
        self.assertEqual(report.recommended_power_dbm, 30)


if __name__ == "__main__":
    unittest.main()
