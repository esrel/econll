# ChangeLog

This project adheres to [Semantic Versioning](https://semver.org/).

## 0.4.0 packaging update

2026.11.13

- added `pyproject.toml` (removing `setup.py` & `requirements.txt`)
- removed unused `pyyaml` & `setuptools` pins (no runtime dependencies)
- added GitHub workflows (`package`, `publish`)
- fixed license metadata: GPL-3.0-or-later (as in `LICENSE`)
- removed module meta data (`__author__`, `__version__`, etc.)
- type pass:
  - added `typedefs` (type aliases) & `py.typed`; `mypy --strict` passes (config in `pyproject.toml`)
  - modernized hints: `T | None` instead of implicit `Optional`, `Sequence`/`Mapping` inputs, fixed wrong annotations (`select`, `convert`, `guess`)
  - replaced `**kwargs` forwarding with explicit `kind`, `glue` & `otag` parameters
  - removed `:type:`/`:rtype:` from docstrings (duplicated hints)
  - `rebase`: tag format params (`kind`, `glue`, `otag`) are now respected
  - `scheme_tagset`: tag format params are now respected
- fixed input validation: `align`, `rebase` & `rebase_tokens` raise `ValueError` (not `assert`);
  `align` checks coverage w.r.t. tokens (not characters of a string input)
- `rebase`:
  - warns about removed chunks (`UserWarning: removed chunks (not on source token boundaries): [...]`)
  - preserves IOB1 & IOE1 schemes (guesses with `guess_scheme_one`)
- fixed `xcode`: overlapping or out-of-range chunks raise `ValueError`; `length=0` is respected
- fixed `index_tokens`: `ValueError` if a token is not in the source; `merge_pieces` handles no pieces
- fixed `report`: integer column width accounts for total counts
- replaced `list.count` loops with `Counter` in `scorer` (`count_stats`)
- fixed `converter`:
  - `from_conll`: supports any number of columns (token is the first, tag is the last)
  - tag format (`fmt`: `kind`, `glue`, `otag`) for `conll` in `convert`, `from_conll` & `make_conll`
  - `from_parse`: raises `ValueError` if there is no text (not `'None'`); span keys default to `label`, `bos`, `eos`, `value` (not dict order); `maps` consistently maps canonical keys to data keys
  - `make_mdown`: raises `ValueError` for overlapping spans & unwritable labels/values; accepts spans without a value
  - `from_mdown`: added `regex` param (as `has_mdown`)
- fixed CLI:
  - added `econll` console script; `prog` is `econll`
  - `conv` requires `-o`; passes tag & data format params; `stat` honors tag format
  - `read` skips empty lines; `save` keeps non-ASCII characters
  - `main` accepts `argv`
- fixed `decisor`:
  - `consolidate`: a span containing (or contained in) a better span is an overlap (`overlaps`)
  - `group_spans`: returns indices of the input spans (not of the sorted ones)
- fixed `scorer` & `stats` for data with no classes/chunks: no crashes (`macro`/`weighted` are 0.0)
- fixed `load`:
  - the last block is kept when the file has no trailing boundary line
  - trailing empty fields are preserved
  - `docstart` matches the first field of a line (`-DOCSTART- -X- -X- O`)
- fixed `parse_tag`: labels can contain `glue` (`B-New-York`); malformed tags raise `ValueError`

## 0.3.1
- fixed `mdown` reading: a bracket of the text (`[ [a](x) ]`) is a word, not the start of a chunk; a chunk can be a bracket token (`[[](PUNCT)`)
- made the `mdown` pattern a constant (`converter.MDOWN`)

## 0.3.0
- added `stats` for computing data statistics
- added `stat` command to CLI
- added linter comments to `converter` and `tabler`

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