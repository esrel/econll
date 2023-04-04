# ChangeLog

This project adheres to [Semantic Versioning](https://semver.org/).

## Aligner
- added aligner methods and tests
- added `annotation_transfer.md` into `docs`
- updated token with magic methods `__len__` and `__contains__`
- updated token `update` to support `dict` of params
- added IOB1 & IOE1 support

## Unreleased
- updated README.md
- added CHANGELOG.md
- added `bos` and `eos` attributes to `Chunk` and `Token` to hold character indices
- added `make_tagset` token method to generate tagset from a set of labels and scheme string
- added public functions `chunk_eval`, `token_eval`, `convert_scheme`, `correct_tags` to `__init__.py`
- removed `style`, `margin`, etc. from reporting and command-line
- updated token & chunk methods for better modularization
- updated scoring methods to output full report, including predicted and correct counts
- updated report table to accommodate full report
- changed chunk methods to work at block level
- changed `evaluate` to be in-line with `chunk_eval` and `token_eval`
- removed `correct` command from CLI
- separated parsing/merging from modifications (reaffix/relabel/convert)

## 0.1.2

- installation fixes

## 0.1.1

- installation fixes

## 0.1.0

- initial release