import os

import pytest

from w4h_sample_icde_demo_csv_importer.client import W4HClient


@pytest.mark.integration
def test_import_subjects_batch():
    if not os.environ.get("W4H_API_KEY", "").strip():
        pytest.skip("W4H_API_KEY not set")
    dataset_id = os.environ.get("W4H_DATASET_ID", "sample-icde-demo-csv")
    client = W4HClient()
    result = client.import_csv_batch(
        dataset_id,
        {
            "signal": "subjects",
            "table_prefix": "icde_demo",
            "mode": "append",
            "dedupe_columns": ["id"],
            "columns": [
                {"name": "id", "type": "text"},
                {"name": "start_date", "type": "date"},
                {"name": "end_date", "type": "date"},
            ],
            "rows": [{"id": "test-subj", "start_date": "2020-01-01", "end_date": "2020-01-02"}],
            "source_name": "ICDE demo",
            "description": "integration test row",
        },
    )
    assert result.get("success") is True


@pytest.mark.integration
def test_import_gps_track_batch_coerces_malformed_latitude():
    """Known ICDE fixture: latitude may hold a Python tuple repr. Ingest should
    store null for unparseable doubles instead of 500ing (vendor-spec misfit is
    reported separately by the importer)."""
    if not os.environ.get("W4H_API_KEY", "").strip():
        pytest.skip("W4H_API_KEY not set")
    dataset_id = os.environ.get("W4H_DATASET_ID", "sample-icde-demo-csv")
    client = W4HClient()
    result = client.import_csv_batch(
        dataset_id,
        {
            "signal": "gps_track",
            "table_prefix": "icde_demo",
            "mode": "append",
            "dedupe_columns": ["id", "date", "timestamp"],
            "columns": [
                {"name": "id", "type": "text"},
                {"name": "date", "type": "date"},
                {"name": "timestamp", "type": "text"},
                {"name": "latitude", "type": "double precision"},
                {"name": "longitude", "type": "double precision"},
            ],
            "rows": [
                {
                    "id": "test-subj-tuple-fixture",
                    "date": "2020-01-01",
                    "timestamp": "00:05:00",
                    "latitude": "(34.0224, -118.2851)",
                    "longitude": "",
                }
            ],
            "source_name": "ICDE demo",
            "description": "integration test malformed geo row",
        },
    )
    assert result.get("success") is True
    assert result.get("inserted") == 1


@pytest.mark.integration
def test_import_gps_track_batch_uses_icde_demo_prefix():
    """Confirms the fixed /import/csv-batch no longer hardcodes 'fitbit_' as
    the physical table prefix (ADR-016 changelog, 2026-08-21)."""
    if not os.environ.get("W4H_API_KEY", "").strip():
        pytest.skip("W4H_API_KEY not set")
    dataset_id = os.environ.get("W4H_DATASET_ID", "sample-icde-demo-csv")
    client = W4HClient()
    result = client.import_csv_batch(
        dataset_id,
        {
            "signal": "gps_track",
            "table_prefix": "icde_demo",
            "mode": "append",
            "dedupe_columns": ["id", "date", "timestamp"],
            "columns": [
                {"name": "id", "type": "text"},
                {"name": "date", "type": "date"},
                {"name": "timestamp", "type": "text"},
                {"name": "latitude", "type": "double precision"},
                {"name": "longitude", "type": "double precision"},
            ],
            "mapping": {
                "signal_type": "gps_track",
                "subject": "id",
                "time": {"combine": ["date", "timestamp"]},
                "geo": {"lat": "latitude", "lon": "longitude"},
                "values": [],
            },
            "rows": [
                {
                    "id": "test-subj",
                    "date": "2020-01-01",
                    "timestamp": "00:00:00",
                    "latitude": "34.0224",
                    "longitude": "-118.2851",
                }
            ],
            "source_name": "ICDE demo",
            "description": "integration test row",
        },
    )
    assert result.get("success") is True
    assert result.get("physical_table") == "icde_demo_gps_track"
