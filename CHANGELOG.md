# ChangeLog

This project adheres to [Semantic Versioning](https://semver.org/).

## 0.2.5

- refactored `convert`
- removed `labels` from `refs`

## 0.2.4
- added CLI interface to `convert`
- added reference label input for `convert` (reusing `refs`)
- added JSONL, YAML, & LIST rile reading to `__main__`

## 0.2.3
- added conversion (`convert`) to/from CoNLL data (`conll`):
  - YAML/Markdown format (`mdown`)
  - JSON/JSONL parse (`parse`)

## 0.2.2
- added support for WordPiece tokenization indexing

## 0.2.1
- added `xcoder` functions and tests

## 0.2.0
- major refactoring
- removed dataclasses (temporarily)
- removed all but evaluation from CLI
- added CHANGELOG.md
- added "IOB1" & "IOE1" support
- added `aligner` functions and tests
- added `rebaser` functions and tests
- added `decisor` functions and tests
- added `schemer` functions and tests
- added `demo` folder for jupyter notebooks
- added `docs` folder for documentation

## 0.1.2
- installation fixes

## 0.1.1
- installation fixes

## 0.1.0
- initial release