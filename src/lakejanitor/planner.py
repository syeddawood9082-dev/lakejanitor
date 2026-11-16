"""Dry run maintenance plans for one Iceberg table.

The plan is ordered the way a careful engineer would run the work.
Manifest rewrites come first because they make planning cheaper for
every step after them. Compaction comes next. Snapshot expiry comes
last and only when the oldest snapshot is past the retention window.
Nothing in here runs a step. The plan is advice with reasons.
"""

from .models import PlanStep
from .scoring import DELETE_RATIO_WARN, MANIFEST_COUNT_WARN, SNAPSHOT_COUNT_WARN, TARGET_DATA_FILE_BYTES

RETENTION_DAYS = 7


def build_plan(summary, findings):
    """Return the ordered plan steps for one table."""
    codes = {finding.code for finding in findings}
    steps = []

    if "many-manifests" in codes:
        steps.append(
            PlanStep(
                action="Rewrite manifests so planning reads fewer files first",
                reason=f"{summary.manifest_count} manifests slow down every plan this table makes",
                estimated_saving="Faster query planning on every read",
            )
        )

    if codes & {"small-data-files", "undersized-data-files"}:
        target_files = max(summary.data_file_total_bytes // TARGET_DATA_FILE_BYTES, 1)
        steps.append(
            PlanStep(
                action="Compact small data files into target sized files",
                reason="Small files make readers open far more files than the data needs",
                estimated_saving=(
                    f"About {summary.data_file_count} files down to about {target_files} "
                    "target sized files"
                ),
            )
        )

    if "oversized-data-files" in codes:
        steps.append(
            PlanStep(
                action="Split oversized data files into target sized files",
                reason="Oversized files leave readers with too little work to share across tasks",
                estimated_saving="Reads spread across more tasks at the same total size",
            )
        )

    if codes & {"delete-files-heavy", "delete-files-growing"}:
        steps.append(
            PlanStep(
                action="Rewrite data files that carry the most deletes",
                reason="Delete files force readers to filter rows that are already gone",
                estimated_saving=f"{summary.delete_file_count} delete files merged away",
            )
        )

    if codes & {"many-snapshots", "stale-snapshots"} or summary.snapshot_count > SNAPSHOT_COUNT_WARN:
        hold = ""
        if summary.oldest_snapshot_age_days < RETENTION_DAYS:
            hold = (
                f"The oldest snapshot is {summary.oldest_snapshot_age_days:.0f} days old "
                f"and the retention window is {RETENTION_DAYS} days, so expiry should wait"
            )
        steps.append(
            PlanStep(
                action="Expire snapshots past the retention window",
                reason=f"{summary.snapshot_count} snapshots are still retained",
                estimated_saving="Metadata and orphaned files reclaimed",
                hold_reason=hold,
            )
        )

    if not steps:
        steps.append(
            PlanStep(
                action="No maintenance needed right now",
                reason="The metadata shows no problem worth spending compute on",
                estimated_saving="Nothing spent and nothing needed",
            )
        )
    return steps
