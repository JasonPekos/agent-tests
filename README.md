# agent-tests

Personal eval lab: custom benchmarks for LLM agents, run locally with Docker
via [harbor](https://harborframework.com) (`uv tool install harbor`).

```
harbor-tasks/     one directory per task (vendor/ = pristine upstream copies)
jobs/             harbor run output (gitignored — harvest before deleting)
analysis/         harvest.py + trials.csv (committed, one row per trial)
notes/            one writeup per experiment (see notes/TEMPLATE.md)
```

## The whole mental model

A **task** is a directory: a Dockerfile (the world), `instruction.md` (the
prompt), `tests/test.sh` (the grader), `solution/solve.sh` (a known-good
answer). A **trial** runs in five steps, all inside a throwaway container:

1. build the Dockerfile, start a container for this trial
2. install the agent CLI inside it (claude-code, codex, ...)
3. run the CLI headlessly with `instruction.md`; it does whatever it wants —
   the harness just waits (all model calls happen inside, on the CLI's own auth)
4. copy `tests/` in (only now, so the agent can't peek) and run `test.sh`,
   which writes a reward in [0, 1] to `/logs/verifier/reward.txt`
5. tear down the container; logs and reward land in `jobs/<job>/<trial>/`

The `oracle` agent runs `solution/solve.sh` instead of a model — if oracle
doesn't score 1.0, the task is broken, not the agent.

## Commands

```bash
harbor init --task jason/my-task                 # scaffold a new task (in harbor-tasks/)
harbor run -p harbor-tasks/hello-harbor -a oracle          # validate the task itself
harbor run -p harbor-tasks/hello-harbor -a claude-code \
  -m anthropic/claude-sonnet-5 --env-file .env             # real run (subscription-billed)
harbor view                                      # web UI over jobs/trajectories
python3 analysis/harvest.py                      # jobs/ -> analysis/trials.csv
docker system prune -af --filter "until=168h"    # reclaim disk from old images
```

Useful `harbor run` flags: `-m` repeatable (multi-model), `-k N` attempts per
task, `-n N` concurrency, `-i 'glob'` task filter.

## Auth

`.env` (gitignored) holds `CLAUDE_CODE_OAUTH_TOKEN` (from `claude setup-token`)
plus `CLAUDE_FORCE_OAUTH=1` — claude-code runs bill the subscription, not API.
API-billed agents want `ANTHROPIC_API_KEY` / `OPENROUTER_API_KEY` there instead.

## Run-design rules (so the stats work later)

1. Always `-k >= 4` attempts per task — variance decomposition and pass^k need
   replication; subscription attempts are ~free.
2. Compare models only within one job (same task set, same config).
3. Keep infra errors distinct from reward=0 — decide exclusions at analysis
   time, not collection time.
4. Every task declares `difficulty` and `family` in `[metadata]` — clustered
   SEs and IRT need the labels.
