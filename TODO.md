# eCoNLL TODOs

## General Functionality

- ADD baselines
  - standard baselines: majority, random, chance
  - computed baselines:
    - MLE, MLE + Priors
    - 1-gram, 2-gram for transitions

## I/O & Data Formats

### `reader`

- ADD json/jsonl format support
- ADD CoNLL-JSON data conversion (e.g. `rasa` NLU)

### `parser`

## Evaluation

### `scorer`

- ADD partial span match evaluation (extend `compute_spans_stats`)

### `tabler`

## Hypotheses & Reference Alignment

### `indexer`
- ADD indexing (`index`) with token substitutions (Levenshtein over tokens) for alignment

### `aligner`

### `rebaser`

- FIX removed chunks warnings: improve informativeness (`UserWarning: removed chunks: [('y', 2, 3)]`)
- ADD tokens to strip from a chunk span for `rebase_chunks`

## Hypothesis Selection/Computation

### `decisor`

## Utilities

### `schemer`