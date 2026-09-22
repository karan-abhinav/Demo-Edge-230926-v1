---
name: pipeline-audit
description: Audit an embedded telemetry pipeline end to end - ingest, feature extraction, detection, persistence - and report correctness and robustness risks. Use when asked to audit, harden, or review a data pipeline as a whole rather than a single file.
---

# Pipeline audit

Audit the pipeline as a system, not file by file. Run the four stages below in
parallel subagents so the reading stays out of the main conversation, then
synthesise one report.

## Stages

1. **Ingest** — encoding, delimiter, and type-coercion failures. Does a
   malformed row raise, or silently become a zero?
2. **Features** — window boundaries, empty and single-element inputs, division
   by zero, NaN propagation.
3. **Detection** — threshold provenance, sensitivity to scale, what happens
   when every sample is identical.
4. **Persistence** — schema drift, transaction boundaries, SQL built by string
   concatenation.

## Report

For each stage give: what you read, the highest-severity finding, a
reproduction (input that triggers it), and the fix. Rank all findings across
stages into one ordered list at the end. If a stage is clean, say so in one
line rather than padding it.
