import pytest

from w4h_sample_icde_demo_csv_importer.config import sample_package_path
from w4h_sample_icde_demo_csv_importer.csv_import import iter_csv_rows
from w4h_sample_icde_demo_csv_importer.manifest import load_manifest, signal_by_slug
from w4h_sample_icde_demo_csv_importer.vendor_spec import MisfitTracker, check_row


def test_type_mismatch_detected():
    columns = [{"name": "value", "type": "double precision"}]
    misfits = check_row(columns, None, None, {"value": "not-a-number"})
    assert misfits == [
        {
            "type": "type_mismatch",
            "column": "value",
            "detail": "value 'not-a-number' does not match declared type 'double precision'",
        }
    ]


def test_valid_values_produce_no_misfits():
    columns = [{"name": "latitude", "type": "double precision"}, {"name": "longitude", "type": "double precision"}]
    assert check_row(columns, None, None, {"latitude": "34.0224", "longitude": "-118.2851"}) == []


def _package_root():
    return sample_package_path()


def test_catches_known_gps_track_tuple_fixture():
    """Known fixture, carried over from the source w4h-icde-demo dataset (not
    manufactured for this sample): subjects 4c9fe48e and 84d5380c have their
    `latitude` column holding a Python tuple repr "(lat, lon)" with
    `longitude` empty — a real bug in that prototype's synthetic data
    generator. Left in on purpose (see README) so vendor-spec checking has a
    real geo-malformation to catch. Subject c12574be is unaffected."""
    package_root = _package_root()
    if not (package_root / "manifest.yaml").is_file():
        pytest.skip("w4h-sample-icde-demo-csv not checked out beside importer")

    manifest = load_manifest(package_root)
    signal = signal_by_slug(manifest, "gps_track")
    csv_path = package_root / signal["file"]
    columns = signal["columns"]
    mapping = signal["geomts_mapping"]
    sampling_interval = signal.get("sampling_interval")

    tracker = MisfitTracker()
    for chunk in iter_csv_rows(csv_path):
        for row in chunk:
            tracker.record(row, check_row(columns, mapping, sampling_interval, row))

    [entry] = tracker.summary()
    assert entry["type"] == "type_mismatch"
    assert entry["column"] == "latitude"
    assert entry["count"] == 1728  # 2 of 3 subjects x 864 rows each


def test_no_misfits_in_heart_rate_sample():
    package_root = _package_root()
    if not (package_root / "manifest.yaml").is_file():
        pytest.skip("w4h-sample-icde-demo-csv not checked out beside importer")

    manifest = load_manifest(package_root)
    signal = signal_by_slug(manifest, "heart_rate")
    csv_path = package_root / signal["file"]
    columns = signal["columns"]
    mapping = signal["geomts_mapping"]
    sampling_interval = signal.get("sampling_interval")

    tracker = MisfitTracker()
    for chunk in iter_csv_rows(csv_path):
        for row in chunk:
            tracker.record(row, check_row(columns, mapping, sampling_interval, row))

    assert tracker.total == 0
