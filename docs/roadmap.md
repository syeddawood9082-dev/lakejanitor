# Roadmap

Work is grouped by how close it is. Items move to the changelog when they ship.

## Now

- Health score and dry run plan from a JSON table summary, shipped as the scaffold
- PyIceberg reader that builds the summary from real table metadata, with the metadata mapping layer shipped and tested ahead of it
- A sample summary for the orders table so the demo runs with no catalog at all
- Markdown and JSON report output beside the plain text report, with a format flag on the check command
- Findings that keep growing one problem at a time, with the delete file family now split into equality and position delete counts so each kind names its own cost

## Next

- Schema drift timeline read from the metadata log
- A check command that reads a whole catalog and reports every table in it

## Later

- Partition health notes that flag partitions carrying far more files than their neighbours
- A history file so a team can watch a table score move week over week

## Not planned

- Executing maintenance steps. The planner stays a planner until a separate decision says otherwise.
- A web dashboard. The report is text a person can paste into a ticket on purpose.
