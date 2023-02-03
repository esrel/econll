# TODOs

## Processing

- Add possibility to convert CoNLL data to JSON (e.g. `rasa`)
  Requires, token indexing for raw text.

## Reporting

- Modify `print_table` to support `stats` reporting & `score` reporting at the same time.
  Requires, variable number of columns and cell types, which are currently fixed.
  **Alternative**: switch to `beautifultable`
- Fix header cell alignment for numeric fields for `md` table.
- Add LaTeX table style