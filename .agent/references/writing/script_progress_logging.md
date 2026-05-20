# Script Progress Logging Reference

Use this reference only when writing scripts that fetch, parse, or transform data.

## Core Rules

- Emit progress messages throughout long-running work.
- Use `log.info` or the project-equivalent structured logger, not silent loops.
- Include enough context to debug partial failures:
  current batch, current item, counts completed, counts failed, and retry state.
- Log final summary counts before exit.

## Good Progress Signals

- total items discovered
- current batch number and batch size
- current item identifier
- percentage complete or completed/total
- skipped item reason
- final success/failure totals

## Goal

Scripts should be inspectable by a later agent without rerunning the whole job blindly.
