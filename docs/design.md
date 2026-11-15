# Design

## The problem

Iceberg tables degrade quietly. Writers append small files because streaming jobs commit often. Deletes land as separate delete files because merge on read is the default for a reason. Snapshots pile up because nobody wants to be the person who expired the one snapshot a rollback needed. None of this is a bug. All of it makes reads slower a little at a time until a table that answered in seconds answers in minutes.

The tools in the stack will run the maintenance once a person decides what to run and in what order. That decision is the gap. It needs a read of the metadata, a judgement about which problems matter, and a sense of order so one step does not waste the compute another step just spent.

## The shape of the answer

LakeJanitor reads metadata and nothing else. It scores the table, names the reasons, and prints a plan. A person or a scheduler takes the plan from there.

Three choices shape the first version.

The first choice is read only. A planner can run against production tables from a laptop with no change window, no lock, and no risk. Trust comes first and execution can be added later behind the same plan shape if it ever belongs here at all.

The second choice is an explainable score. Every finding carries the counts that produced it. When a table scores 62 the report says which files and which ratios cost the points. A team can disagree with a threshold and change it. A team cannot use a score it cannot see inside.

The third choice is an ordered plan with holds. Steps run in the order that wastes the least compute. A step that should wait stays in the plan with its hold reason written out, because a plan that hides a step teaches nobody anything.

## What the first version reads

The summary shape in the code is the whole input. File counts and sizes, delete file counts, manifest counts, snapshot counts and ages, and schema change counts. Every one of those values sits in Iceberg metadata today, so the PyIceberg reader that fills the summary is a mapping job and not a research project.

## The second use case

A schema drift timeline reads the metadata log and shows when each schema change landed and what it changed. Teams feel schema drift as surprise breakage in downstream jobs. A timeline turns that surprise into a record they can read before the next change lands. It ships after the health check because the health check is the daily pain and the timeline is the weekly one.

## What this will not do

It will not execute maintenance in the first version. It will not guess at query patterns it cannot see in metadata. It will not score a table against tables owned by other teams, because a health score is about one table against its own target shape and nothing else.
