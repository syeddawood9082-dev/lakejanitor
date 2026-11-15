# Summary format

The check command reads a JSON file that describes one table, or a list of files that each describe one table. Every field except the name is optional and defaults to zero.

```json
{
  "name": "orders",
  "data_file_count": 412,
  "data_file_total_bytes": 7785676800,
  "delete_file_count": 96,
  "manifest_count": 240,
  "snapshot_count": 300,
  "oldest_snapshot_age_days": 30.0,
  "current_schema_column_count": 18,
  "schema_change_count": 4,
  "record_count": 9200000
}
```

Field notes, in plain words.

- name is the table name as a person would say it.
- data_file_count and data_file_total_bytes drive the small file findings. The average file size is the total divided by the count.
- delete_file_count is read against the data file count as a ratio.
- manifest_count drives the planning cost finding.
- snapshot_count and oldest_snapshot_age_days drive the expiry step and its hold.
- current_schema_column_count and schema_change_count drive the wide schema and frequent schema change findings, and they also feed the schema drift timeline that ships next.
- record_count drives the low records per file and empty data files findings.
- equality_delete_file_count and position_delete_file_count each drive their own delete file finding when the count runs past ten.
