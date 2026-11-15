# LakeJanitor

LakeJanitor is a read only health check for Apache Iceberg tables. It reads table metadata through PyIceberg and tells you how healthy each table is and what maintenance would help, in plain English, before you spend any compute on it.

Most Iceberg tables do not break. They slowly fill up with small files and delete files until every query pays for work nobody planned. The fix is usually simple once somebody can see the shape of the problem. LakeJanitor is that look.

## What it does

- Scores each table from 0 to 100 based on the metadata alone
- Names the reasons behind the score in plain English
- Prints a dry run maintenance plan in the order a careful engineer would run it
- Estimates the savings each step should bring
- Warns when a step should not run yet and says why
- Never writes to a table. The first version is a planner and nothing else

## A quick look at the output

```text
orders  score 52
  Many small data files. 412 data files average 18 MB against a 128 MB target
  Delete files are growing. 96 delete files against 412 data files
Plan for orders
  1. Rewrite manifests so planning reads fewer files first
  2. Compact small data files into target sized files
  3. Hold off on snapshot expiry until the oldest snapshot is past the retention window
```

## Run it

You need Python 3.11 or newer.

```bash
pip install -e ".[dev]"
lakejanitor check --summary summary.json
lakejanitor check --summary summary.json --format markdown
lakejanitor check --summary summary.json --format json
```

The report prints as plain text by default. The Markdown form drops into a pull request or a ticket as it is, and the JSON form feeds whatever tool a team already reads.

The summary file is a small JSON document that describes one table at a time. The shape is documented in docs/summary-format.md. A PyIceberg reader that builds the summary straight from table metadata is the next piece of work and it lands behind the same summary shape, so the scoring and planning code never changes when the reader arrives.

## Run the tests

```bash
pytest
ruff check src tests
```

## How it is put together

| Path | What lives there |
| --- | --- |
| `src/lakejanitor/models.py` | The table summary, finding, and plan step shapes |
| `src/lakejanitor/scoring.py` | The health score and the plain English reasons |
| `src/lakejanitor/planner.py` | The dry run plan and the warnings that hold steps back |
| `src/lakejanitor/report.py` | The plain text report a person reads |
| `src/lakejanitor/cli.py` | The command line entry point |
| `src/lakejanitor/reader.py` | The mapping from a metadata export shape to a table summary |
| `docs/design.md` | Why the tool is read only and planner first |
| `docs/roadmap.md` | What ships next and in what order |

## Design choices worth knowing

- Read only on purpose. A tool that only reads metadata can run anywhere, against production tables, with no change window and no risk of making a slow table worse.
- The score is explainable. Every point lost names a finding, and every finding names the numbers behind it. A score nobody can explain is a score nobody trusts.
- The plan is ordered. Manifest rewrites come before compaction, and snapshot expiry comes last, because running those steps out of order wastes compute.
- Warnings are part of the plan. A step that should wait says so in the plan itself instead of quietly disappearing.

## Where this goes next

Planned, in order:

1. A PyIceberg reader that builds table summaries from real metadata
2. A schema drift timeline read from the metadata log

Each of those lands as its own small change, per CONTRIBUTING.md.

## License

MIT. See LICENSE.
