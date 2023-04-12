# eCoNLL TODOs

### `indexer`
- ADD indexing (`index`) with token substitutions (Levenshtein over tokens) for alignment

### `rebaser`

- FIX removed chunks warnings: improve informativeness (`UserWarning: removed chunks: [('y', 2, 3)]`)
- ADD tokens to strip from a chunk span for `rebase_chunks`

### `scorer`

- ADD baselines: random, chance, majority (HMM?)
- ADD partial span match evaluation (extend `compute_spans_stats`)