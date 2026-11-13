# eCoNLL TODOs

### `indexer`
- ADD indexing (`index`) with token substitutions (Levenshtein over tokens) for alignment

### `rebaser`

- FIX removed chunks warning: it now reports the chunks (`UserWarning: removed chunks (not on source token boundaries): [('y', 2, 3)]`);
  improve informativeness further: show the tokens of the removed chunks (needs tokens in `rebase_chunks`)
- ADD tokens to strip from a chunk span for `rebase_chunks`

### `scorer`

- ADD baselines: random, chance, majority (HMM?)
- ADD partial span match evaluation (extend `compute_spans_stats`)
- ADD `zero_division` option to `score` (currently precision is 1.0 if there are no predictions, and recall is 0.0 if there are no gold items; see `sklearn`)

### `converter`

- ADD escaping for `mdown` labels & values that contain `:` or `)` (currently `make_mdown` raises `ValueError`)

### project

- REPLACE `flake8` with `ruff` in CI (the `--exit-zero` step never fails the build); add `[tool.ruff]` to `pyproject.toml`
- CONVERT docstrings to Google style (`:type:`/`:rtype:` lines were removed as they duplicated the type hints)
- AUDIT `docs/` (Sphinx) and `demo/evaluation.ipynb` for staleness w.r.t. the 0.4.0 API
