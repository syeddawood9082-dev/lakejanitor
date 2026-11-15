# Changelog

All notable changes to this project are recorded here. The format follows the spirit of Keep a Changelog and the versions follow semantic versioning.

## Unreleased

- Metadata reader mapping for the delete file split and the partition, orphan file, and metadata file counts so a reader export scores with the full finding set

- Metadata files finding that names the count when metadata files build up past one hundred files
- Position delete files finding that names the count when position deletes build up past ten files
- Metadata reader mapping that builds a table summary from file and snapshot entries in a reader export shape
- JSON and Markdown report output beside the plain text report, with a format flag on the check command
- Health score with plain English findings for small files, delete files, manifests, and snapshots
- Dry run maintenance plan with ordered steps, estimated savings, and hold reasons
- Check command that reads a JSON table summary and prints the report
- Design notes and roadmap

## 0.1.0

- Not released yet. The scaffold is built and tested on the author machine and ships when the repo is created.
