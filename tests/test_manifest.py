import pytest

from w4h_sample_icde_demo_csv_importer.config import sample_package_path
from w4h_sample_icde_demo_csv_importer.csv_import import _dedupe_columns_for_signal
from w4h_sample_icde_demo_csv_importer.manifest import load_manifest, signal_by_slug


@pytest.fixture
def package_root():
    return sample_package_path()


def test_manifest_loads(package_root):
    if not (package_root / "manifest.yaml").is_file():
        pytest.skip("w4h-sample-icde-demo-csv not checked out beside importer")
    manifest = load_manifest(package_root)
    assert manifest["vendor"] == "icde-demo"
    assert len(manifest["signals"]) == 8


def test_signal_slugs(package_root):
    if not (package_root / "manifest.yaml").is_file():
        pytest.skip("w4h-sample-icde-demo-csv not checked out beside importer")
    manifest = load_manifest(package_root)
    slugs = [s["slug"] for s in manifest["signals"]]
    assert slugs == [
        "subjects",
        "heart_rate",
        "calories",
        "distances",
        "steps",
        "sleep",
        "weight",
        "gps_track",
    ]
    for slug in slugs:
        signal = signal_by_slug(manifest, slug)
        csv_path = package_root / signal["file"]
        assert csv_path.is_file(), f"missing {csv_path}"


def test_gps_track_has_geo_mapping(package_root):
    if not (package_root / "manifest.yaml").is_file():
        pytest.skip("w4h-sample-icde-demo-csv not checked out beside importer")
    manifest = load_manifest(package_root)
    gps = signal_by_slug(manifest, "gps_track")
    mapping = gps["geomts_mapping"]
    assert mapping["geo"] == {"lat": "latitude", "lon": "longitude"}


def test_non_geo_signals_declare_geo_null(package_root):
    if not (package_root / "manifest.yaml").is_file():
        pytest.skip("w4h-sample-icde-demo-csv not checked out beside importer")
    manifest = load_manifest(package_root)
    for slug in ["heart_rate", "calories", "distances", "steps", "sleep", "weight"]:
        signal = signal_by_slug(manifest, slug)
        assert signal["geomts_mapping"]["geo"] is None


def test_dedupe_columns_for_signals():
    assert _dedupe_columns_for_signal("subjects") == ["id"]
    assert _dedupe_columns_for_signal("heart_rate") == ["id", "date", "timestamp"]
    assert _dedupe_columns_for_signal("gps_track") == ["id", "date", "timestamp"]
    assert _dedupe_columns_for_signal("unknown") == ["id", "date", "timestamp"]
