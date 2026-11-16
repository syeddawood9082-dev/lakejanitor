"""Health scoring for one Iceberg table summary.

The score starts at 100 and loses points for each problem the metadata
shows. Every point lost is tied to a finding that names the numbers
behind it, so a reader can argue with the score using the same facts
the score used.
"""

from .models import Finding, TableSummary

TARGET_DATA_FILE_BYTES = 128 * 1024 * 1024
SMALL_FILE_FRACTION = 0.25
DELETE_RATIO_WARN = 0.10
DELETE_RATIO_HEAVY = 0.25
EQUALITY_DELETE_WARN = 10
POSITION_DELETE_WARN = 10
MANIFEST_COUNT_WARN = 100
SNAPSHOT_COUNT_WARN = 100
SNAPSHOT_AGE_WARN_DAYS = 90.0
SCHEMA_CHANGE_WARN = 10
OVERSIZED_FILE_BYTES = 2 * TARGET_DATA_FILE_BYTES
RECORDS_PER_FILE_WARN = 100
RECORDS_PER_FILE_HIGH_WARN = 1000000
PARTITION_COUNT_WARN = 1000
COLUMN_COUNT_WARN = 200
ORPHAN_FILE_WARN = 10
METADATA_FILE_WARN = 100


def score_table(summary):
    """Return a score from 0 to 100 plus the findings behind it."""
    findings = []

    if summary.data_file_count > 0:
        average = summary.average_data_file_bytes
        small_limit = int(TARGET_DATA_FILE_BYTES * SMALL_FILE_FRACTION)
        if average < small_limit:
            findings.append(
                Finding(
                    code="small-data-files",
                    message=(
                        f"Many small data files. {summary.data_file_count} data files "
                        f"average {average // (1024 * 1024)} MB against a 128 MB target"
                    ),
                    points_lost=20,
                )
            )
        elif average < TARGET_DATA_FILE_BYTES:
            findings.append(
                Finding(
                    code="undersized-data-files",
                    message=(
                        f"Data files run under target size. {summary.data_file_count} data files "
                        f"average {average // (1024 * 1024)} MB against a 128 MB target"
                    ),
                    points_lost=8,
                )
            )

        elif average > OVERSIZED_FILE_BYTES:
            findings.append(
                Finding(
                    code="oversized-data-files",
                    message=(
                        f"Data files run over target size. {summary.data_file_count} data files "
                        f"average {average // (1024 * 1024)} MB against a 128 MB target"
                    ),
                    points_lost=5,
                )
            )

    ratio = summary.delete_file_ratio
    if ratio >= DELETE_RATIO_HEAVY:
        findings.append(
            Finding(
                code="delete-files-heavy",
                message=(
                    f"Delete files are piling up. {summary.delete_file_count} delete files "
                    f"against {summary.data_file_count} data files"
                ),
                points_lost=20,
            )
        )
    elif ratio >= DELETE_RATIO_WARN:
        findings.append(
            Finding(
                code="delete-files-growing",
                message=(
                    f"Delete files are growing. {summary.delete_file_count} delete files "
                    f"against {summary.data_file_count} data files"
                ),
                points_lost=10,
            )
        )

    if summary.equality_delete_file_count > EQUALITY_DELETE_WARN:
        findings.append(
            Finding(
                code="equality-delete-files",
                message=(
                    f"Equality delete files are building up. {summary.equality_delete_file_count} "
                    "equality delete files force readers to match rows on every scan"
                ),
                points_lost=5,
            )
        )

    if summary.position_delete_file_count > POSITION_DELETE_WARN:
        findings.append(
            Finding(
                code="position-delete-files",
                message=(
                    f"Position delete files are building up. {summary.position_delete_file_count} "
                    "position delete files force readers to skip rows by position on every scan"
                ),
                points_lost=5,
            )
        )

    if summary.manifest_count > MANIFEST_COUNT_WARN:
        findings.append(
            Finding(
                code="many-manifests",
                message=(
                    f"Planning reads a lot of manifests. {summary.manifest_count} manifests "
                    "sit behind this table"
                ),
                points_lost=10,
            )
        )

    if summary.snapshot_count > SNAPSHOT_COUNT_WARN:
        findings.append(
            Finding(
                code="many-snapshots",
                message=(
                    f"Snapshot history is long. {summary.snapshot_count} snapshots "
                    "are still retained"
                ),
                points_lost=8,
            )
        )

    if summary.oldest_snapshot_age_days > SNAPSHOT_AGE_WARN_DAYS:
        findings.append(
            Finding(
                code="stale-snapshots",
                message=(
                    f"Old snapshots are still retained. The oldest snapshot is "
                    f"{summary.oldest_snapshot_age_days:.0f} days old"
                ),
                points_lost=5,
            )
        )

    if summary.schema_change_count > SCHEMA_CHANGE_WARN:
        findings.append(
            Finding(
                code="frequent-schema-changes",
                message=(
                    f"Schema changes are frequent. {summary.schema_change_count} changes "
                    f"sit behind the current schema of {summary.current_schema_column_count} columns"
                ),
                points_lost=5,
            )
        )

    if summary.data_file_count > 0 and summary.record_count > 0:
        records_per_file = summary.record_count // summary.data_file_count
        if records_per_file < RECORDS_PER_FILE_WARN:
            findings.append(
                Finding(
                    code="low-records-per-file",
                    message=(
                        f"Files hold very few records. {summary.record_count} records "
                        f"spread across {summary.data_file_count} data files "
                        f"average {records_per_file} records per file"
                    ),
                    points_lost=5,
                )
            )

    if summary.data_file_count > 0 and summary.record_count > 0:
        records_per_file = summary.record_count // summary.data_file_count
        if records_per_file > RECORDS_PER_FILE_HIGH_WARN:
            findings.append(
                Finding(
                    code="high-records-per-file",
                    message=(
                        f"Files hold very many records. {summary.record_count} records "
                        f"spread across {summary.data_file_count} data files "
                        f"average {records_per_file} records per file"
                    ),
                    points_lost=5,
                )
            )

    if summary.data_file_count > 0 and summary.record_count == 0:
        findings.append(
            Finding(
                code="empty-data-files",
                message=(
                    f"Data files hold no records. {summary.data_file_count} data files "
                    "carry no records at all"
                ),
                points_lost=5,
            )
        )

    if summary.partition_count > PARTITION_COUNT_WARN:
        findings.append(
            Finding(
                code="many-partitions",
                message=(
                    f"Partition count is high. {summary.partition_count} partitions "
                    "spread planning and file pruning across far more groups than readers need"
                ),
                points_lost=5,
            )
        )

    if summary.current_schema_column_count > COLUMN_COUNT_WARN:
        findings.append(
            Finding(
                code="wide-schema",
                message=(
                    f"Schema is very wide. {summary.current_schema_column_count} columns "
                    "make every read carry fields most readers never use"
                ),
                points_lost=5,
            )
        )

    if summary.orphan_file_count > ORPHAN_FILE_WARN:
        findings.append(
            Finding(
                code="orphan-files",
                message=(
                    f"Orphan files are building up. {summary.orphan_file_count} files "
                    "sit in storage with no metadata pointing at them"
                ),
                points_lost=5,
            )
        )

    if summary.metadata_file_count > METADATA_FILE_WARN:
        findings.append(
            Finding(
                code="many-metadata-files",
                message=(
                    f"Metadata files are building up. {summary.metadata_file_count} metadata "
                    "files sit behind this table and every commit adds one more"
                ),
                points_lost=5,
            )
        )

    if summary.data_file_count == 0:
        findings.append(
            Finding(
                code="no-data-files",
                message="The table holds no data files yet",
                points_lost=0,
            )
        )

    score = max(0, 100 - sum(finding.points_lost for finding in findings))
    return score, findings


def summary_from_dict(data):
    """Build a TableSummary from a plain dictionary, ignoring extra keys."""
    known = set(TableSummary.__dataclass_fields__)
    return TableSummary(**{key: value for key, value in data.items() if key in known})
