"""Build a table summary from table metadata shaped like a reader export.

The PyIceberg reader is the planned source for real summaries. This
module is the mapping layer that reader will use. It takes a plain
dictionary that carries file entries and snapshot entries in the shape
a metadata export gives them and returns the TableSummary the scoring
and planning code already understands.

Delete entries may carry a kind of equality or position, and a
metadata export may also list the two delete families on their own
keys. Partition, orphan file, and metadata file counts arrive as
plain numbers. File entries carry a size in bytes and a record count. Snapshot
entries carry a timestamp in milliseconds. Nothing here talks to a
catalog or opens a table, so the mapping is easy to test and the
reader that lands later only has to gather the same facts.
"""

import time

from .models import TableSummary

MS_PER_DAY = 24 * 3600 * 1000


def _file_totals(entries):
    total_bytes = 0
    total_records = 0
    for entry in entries or []:
        if not isinstance(entry, dict):
            continue
        size = entry.get("file_size_in_bytes", entry.get("size", 0))
        records = entry.get("record_count", 0)
        if isinstance(size, (int, float)):
            total_bytes += int(size)
        if isinstance(records, (int, float)):
            total_records += int(records)
    return total_bytes, total_records


def summary_from_metadata(metadata, now_ms=None):
    """Return a TableSummary built from one metadata dictionary.

    Missing pieces read as zero, the same way an empty table reads.
    The oldest snapshot age is measured against now_ms when one is
    given and against the current time otherwise.
    """
    name = metadata.get("name") or "unnamed"
    data_files = metadata.get("data_files") or []
    delete_files = metadata.get("delete_files") or []
    snapshots = metadata.get("snapshots") or []
    total_bytes, total_records = _file_totals(data_files)

    timestamps = []
    for snapshot in snapshots:
        if isinstance(snapshot, dict):
            stamp = snapshot.get("timestamp_ms", snapshot.get("timestamp", 0))
            if isinstance(stamp, (int, float)) and stamp > 0:
                timestamps.append(float(stamp))
    oldest_age = 0.0
    if timestamps:
        reference = float(now_ms) if now_ms is not None else time.time() * 1000
        oldest_age = max(0.0, (reference - min(timestamps)) / MS_PER_DAY)

    equality_files = metadata.get("equality_delete_files") or []
    position_files = metadata.get("position_delete_files") or []
    if not equality_files and not position_files:
        for entry in delete_files:
            if isinstance(entry, dict) and entry.get("kind") == "equality":
                equality_files = [*equality_files, entry]
            elif isinstance(entry, dict) and entry.get("kind") == "position":
                position_files = [*position_files, entry]
    return TableSummary(
        name=name,
        data_file_count=len(data_files),
        data_file_total_bytes=total_bytes,
        delete_file_count=len(delete_files),
        equality_delete_file_count=len(equality_files),
        position_delete_file_count=len(position_files),
        manifest_count=int(metadata.get("manifest_count") or 0),
        snapshot_count=len(snapshots),
        oldest_snapshot_age_days=oldest_age,
        current_schema_column_count=int(metadata.get("current_schema_column_count") or 0),
        schema_change_count=int(metadata.get("schema_change_count") or 0),
        record_count=total_records,
        partition_count=int(metadata.get("partition_count") or 0),
        orphan_file_count=int(metadata.get("orphan_file_count") or 0),
        metadata_file_count=int(metadata.get("metadata_file_count") or 0),
    )
