# TODOs

## Functionality

- Add baselines
- Add partial span match evaluation (extend `compute_span_stats`)

## Processing

- Add possibility to convert CoNLL data to JSON (e.g. `rasa`)
  Requires, token indexing for raw text.
- Add alignment with token substitutions

## Reporting

- Modify `print_table` to support `stats` reporting & `score` reporting at the same time.
  Requires, variable number of columns and cell types, which are currently fixed.
  **Alternative**: switch to `beautifultable`
