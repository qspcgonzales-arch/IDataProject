from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ScanMetrics:
    """Observed scan performance for a scanning technology."""

    range_meters: float
    accuracy: float
    latency_ms: float
    stability: float

    def validate(self) -> None:
        if self.range_meters < 0:
            raise ValueError("range_meters must be non-negative")
        if not 0 <= self.accuracy <= 1:
            raise ValueError("accuracy must be between 0 and 1")
        if self.latency_ms <= 0:
            raise ValueError("latency_ms must be greater than 0")
        if not 0 <= self.stability <= 1:
            raise ValueError("stability must be between 0 and 1")


@dataclass(frozen=True)
class CalibrationSettings:
    """Thresholds used to decide whether T2UHF calibration is successful."""

    target_accuracy: float = 0.95
    target_stability: float = 0.9
    minimum_range_advantage_m: float = 0.5
    maximum_latency_ratio: float = 1.5
    min_power_dbm: int = 5
    max_power_dbm: int = 30
    power_step_dbm: int = 1


@dataclass(frozen=True)
class CalibrationReport:
    """Calibration outcome.

    `beats_barcode` reports whether RFID outperforms the barcode baseline on the
    direct comparison metrics. `meets_targets` reports whether RFID also satisfies
    the configured calibration thresholds. These are related but intentionally
    independent assessments.
    """

    current_power_dbm: int
    recommended_power_dbm: int
    range_advantage_m: float
    latency_ratio: float
    beats_barcode: bool
    meets_targets: bool
    issues: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "current_power_dbm": self.current_power_dbm,
            "recommended_power_dbm": self.recommended_power_dbm,
            "range_advantage_m": self.range_advantage_m,
            "latency_ratio": self.latency_ratio,
            "beats_barcode": self.beats_barcode,
            "meets_targets": self.meets_targets,
            "issues": self.issues,
        }


def evaluate_t2uhf_calibration(
    rfid_metrics: ScanMetrics,
    barcode_metrics: ScanMetrics,
    current_power_dbm: int,
    settings: CalibrationSettings | None = None,
) -> CalibrationReport:
    """Evaluate T2UHF RFID performance against barcode performance."""

    rfid_metrics.validate()
    barcode_metrics.validate()
    settings = settings or CalibrationSettings()

    if settings.min_power_dbm > settings.max_power_dbm:
        raise ValueError("min_power_dbm cannot be greater than max_power_dbm")

    current_power_dbm = max(settings.min_power_dbm, min(current_power_dbm, settings.max_power_dbm))

    issues: list[str] = []
    range_advantage_m = round(rfid_metrics.range_meters - barcode_metrics.range_meters, 3)
    latency_ratio = round(rfid_metrics.latency_ms / barcode_metrics.latency_ms, 3)
    has_accuracy_issue = rfid_metrics.accuracy < settings.target_accuracy
    has_stability_issue = rfid_metrics.stability < settings.target_stability
    has_range_issue = range_advantage_m < settings.minimum_range_advantage_m
    has_latency_issue = latency_ratio > settings.maximum_latency_ratio

    if has_accuracy_issue:
        issues.append("RFID accuracy is below target")
    if has_stability_issue:
        issues.append("RFID stability is below target")
    if has_range_issue:
        issues.append("RFID range does not exceed barcode range by the required margin")
    if has_latency_issue:
        issues.append("RFID latency is too high compared with barcode scanning")
    has_conflicting_signals = has_latency_issue and (
        has_accuracy_issue or has_stability_issue or has_range_issue
    )

    if has_conflicting_signals:
        issues.append("RFID calibration has conflicting power and latency signals")

    recommended_power_dbm = current_power_dbm
    if not has_conflicting_signals and (has_accuracy_issue or has_stability_issue or has_range_issue):
        recommended_power_dbm = min(settings.max_power_dbm, current_power_dbm + settings.power_step_dbm)
    elif not has_conflicting_signals and has_latency_issue:
        recommended_power_dbm = max(settings.min_power_dbm, current_power_dbm - settings.power_step_dbm)

    beats_barcode = (
        range_advantage_m >= settings.minimum_range_advantage_m
        and rfid_metrics.accuracy >= barcode_metrics.accuracy
        and rfid_metrics.stability >= barcode_metrics.stability
    )
    meets_targets = not issues

    return CalibrationReport(
        current_power_dbm=current_power_dbm,
        recommended_power_dbm=recommended_power_dbm,
        range_advantage_m=range_advantage_m,
        latency_ratio=latency_ratio,
        beats_barcode=beats_barcode,
        meets_targets=meets_targets,
        issues=tuple(issues),
    )
