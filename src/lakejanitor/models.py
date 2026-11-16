"""Shapes that carry a table health check through LakeJanitor.

A table summary is everything the scoring and planning code needs to
know about one Iceberg table. The summary is built from metadata alone.
Nothing in this module talks to a catalog or a storage layer, so the
same shapes work for a summary read from a JSON file today and for a
summary built by the PyIceberg reader tomorrow.
"""

from dataclasses import dataclass, field


@dataclass
class TableSummary:
    """One Iceberg table described by its metadata counts and sizes."""

    name: str
    data_file_count: int = 0
    data_file_total_bytes: int = 0
    delete_file_count: int = 0
    equality_delete_file_count: int = 0
    position_delete_file_count: int = 0
    manifest_count: int = 0
    snapshot_count: int = 0
    oldest_snapshot_age_days: float = 0.0
    current_schema_column_count: int = 0
    schema_change_count: int = 0
    record_count: int = 0
    partition_count: int = 0
    orphan_file_count: int = 0
    metadata_file_count: int = 0

    @property
    def average_data_file_bytes(self):
        if self.data_file_count == 0:
            return 0
        return self.data_file_total_bytes // self.data_file_count

    @property
    def delete_file_ratio(self):
        if self.data_file_count == 0:
            return 0.0
        return self.delete_file_count / self.data_file_count


@dataclass
class Finding:
    """One reason behind a health score, with the numbers that prove it."""

    code: str
    message: str
    points_lost: int


@dataclass
class PlanStep:
    """One maintenance step in a dry run plan.

    A step that should wait carries a hold reason instead of being
    dropped from the plan, so a reader sees the full picture.
    """

    action: str
    reason: str
    estimated_saving: str
    hold_reason: str = ""

    @property
    def ready(self):
        return self.hold_reason == ""


@dataclass
class TableHealth:
    """The scored result for one table."""

    summary: TableSummary
    score: int
    findings: list = field(default_factory=list)
    plan: list = field(default_factory=list)
