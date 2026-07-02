# vendor/ — pristine upstream tasks

Tasks copied verbatim from upstream benchmarks, kept unmodified so derivatives
have a clean baseline to diff against. Never edit these in place — derive.

## Provenance

| task | upstream | commit |
|---|---|---|
| `mcmc-sampling-stan` | [laude-institute/terminal-bench-2](https://github.com/laude-institute/terminal-bench-2) (TB 2.0) | `69671fba` (registry pin) |

## Deriving a modified task

Copy out, don't branch in place:

```bash
cp -r harbor-tasks/vendor/mcmc-sampling-stan harbor-tasks/mcmc-noncentered
```

then in the copy: rename it in `task.toml`, set `[metadata]` `family` to link it
to its siblings for the paired stats, edit, and oracle-check. Diff against
vendor/ any time you need to know what you changed.

Note: vendored tasks predate this repo's conventions — they may use the pytest
verifier pattern and richer `[metadata]` (difficulty/category/tags/time
estimates from upstream, worth imitating). Both run fine as-is:

```bash
harbor run -p harbor-tasks/vendor/mcmc-sampling-stan -a oracle
```

Running upstream tasks WITHOUT vendoring (no copy, pulled + pinned by the
registry) also works — vendor only what you intend to fork:

```bash
harbor run -d terminal-bench@2.0 -i mcmc-sampling-stan -a oracle
```
