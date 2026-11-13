# econll 0.4.0 — code assessment

> **Status:** every item in sections 1, 2 and 4 was fixed in 0.4.0 (see `CHANGELOG.md`), except those listed here.
> The test count is now 123 at 98% coverage, with `mypy --strict`, pylint and flake8 clean.
> Not done:
> - the `zero_division` option for `score`
> - the Google-style docstring conversion (the `:type:` lines were removed instead)
> - replacing flake8 with ruff in CI
> - an audit of `docs/` and the demo notebook
>
> The text below is the original assessment, kept for reference.

Scope: all of `src/econll` (15 modules, ~2,000 lines), tests, packaging, CI.
Tools run: pytest + coverage, mypy (default settings), ruff (UP, ANN, B, SIM, PL, D), pylint, flake8, plus targeted probes and a 20k-case fuzz of `chunk`.
Every bug below was reproduced, not just read.

**Overall:** the core tag algebra (`parse`/`chunk`/`xcode`/`alter`) is sound. The fuzz found 0 exceptions on arbitrary IOBES tag sequences, and `chunk` → `xcode` → `chunk` round-trips exactly. The problems sit at the edges: file I/O, error handling, the `**kwargs` plumbing, `converter`, and `decisor`.

## 1. Correctness bugs (by severity)

### High — silent wrong results or data loss

| # | Where | Problem | Reproduction |
|---|-------|---------|--------------|
| 1 | `reader.load` | The last block is dropped when the file has no trailing blank line. There is no flush after the loop. | `"a\tB-X\nb\tI-X\n\nc\tO\nd\tO"` loads 1 block, expected 2 |
| 2 | `reader.load` | `line.strip()` removes trailing separators, so a trailing empty field disappears silently. | `"a\tx\t\n"` loads as `('a','x')` instead of `('a','x','')` |
| 3 | `reader.load` | `docstart` matches the whole line, so CoNLL-2003 `-DOCSTART- -X- -X- O` lines are kept as tokens. | The first block is `[('-DOCSTART- -X- -X- O',)]` |
| 4 | `rebaser.rebase` / `rebase_tokens` | `kind`/`glue`/`otag` are never forwarded to `chunk`, so non-default tag formats give garbage with no error. | `rebase(..., ["O","X-B"], kind="suffix")` returns `['O','B-B','B-I']` |
| 5 | `decisor.consolidate_spans` | The overlap test misses containment, where the best span sits inside a lower-ranked one. The result still overlaps. | `consolidate([(0,10),(2,4)], scores=[1,5], length=False)` returns `[0, 1]` |
| 6 | `decisor.group_spans` | It returns indices into the sorted list, not the input. The test only passes because its input is already sorted. | `group_spans([(5,6),(0,2)])` returns `[[0],[1]]`, expected `[[1],[0]]` |
| 7 | `utils.scheme_tagset` | `merge(...)` is called without `**kwargs`, so `kind`/`glue` are ignored. | `kind="suffix"` still returns `B-X` |

### Medium — crashes and unhelpful errors

- **`parser.parse_tag`**
  - Hyphenated labels (`B-New-York`) raise `too many values to unpack`.
  - A tag with no glue (`PER`) also raises.
  - Fix: `split(glue, 1)` for a prefix and `rsplit(glue, 1)` for a suffix, plus a clear `ValueError`.
- **`scorer.chunkeval` / `tokeneval` / `score_stats`**
  - These raise `TypeError: score() missing 3 required positional arguments` when there are no classes, for example refs and hyps with no chunks.
  - `weighted_average` raises `ZeroDivisionError` when total gold is 0.
- **`stats.stats`** — raises `ValueError: max() arg is empty` when there are no chunks.
- **`aligner.align`**
  - `assert len(source) == ...` uses the string length when `source` is a `str`.
  - Both `aligner` and `rebaser` use `assert` for input validation. It is stripped under `python -O` and raises `AssertionError` instead of `ValueError`.
- **`rebaser.rebase`**
  - It silently drops chunks that don't align. TODO.md already notes this and says "warn", but no warning is emitted.
  - With `source == target` it returns early. That skips the `scheme` conversion and returns the caller's own list object (aliasing).
  - `guess()` can never return IOB1/IOE1, so IOB1 input is silently rewritten as IOB. `guess_scheme_one` exists but is unused and unexported.
- **`xcoder.xcode`** — overlapping chunks are silently overwritten. A chunk past `length` silently grows the list. `length=0` is treated as "unset" because of `or`.
- **`converter`**
  - `from_conll` only handles 2-column rows (`for x, y in data` fails on 3 columns).
  - `from_parse` turns a missing `text` into the string `"None"`.
  - With `keys=None`, span tuples take dict key order, so `{"bos","eos","label","value"}` is silently misread and gives no chunks.
  - `make_mdown` corrupts output for overlapping spans (the text is duplicated).
  - `make_mdown` breaks the round trip when a value contains `)`. A 3-tuple span raises.
  - `has_mdown(regex=...)` accepts a custom regex but `from_mdown` does not.
- **`__main__`**
  - `prog='PROG'` shows in `--help`.
  - `conv` without `-o` crashes with `None` as the path.
  - The tag-format flags (`--kind`, `--glue`, `--otag`) are ignored by `conv` and `stat`.
  - There is no console-script entry point.

### Low / design notes

- `score()` returns precision 1.0 when `pred == 0` but recall 0.0 when `gold == 0`. Add a `zero_division` option and document the convention. As written, an empty-vs-empty class scores F1 = 0.
- `tabler` sizes the integer column from per-class counts only. The totals row (or token counts) can overflow it once counts reach 7 digits.
- `tabler.report` has a docstring that says `colsep` defaults to " " (it is a tab), and a positional-only `/` signature that is awkward to call.
- `index_tokens` uses `source.index(...)`, so a token with internal whitespace passes `check_tokens` and then raises a bare `substring not found`.
- `merge_pieces` fails on an empty list (`reduce` with no initial value).
- O(n²) patterns that are cheap to fix:
  - `chunk` (`i in bos` on a list)
  - `utils.count` (`data.count` per item)
  - `scorer.compute_*_stats` (`gold.count(key)`)
  - `make_conll` (`bos.index`)

## 2. Type hints (outdated / wrong)

mypy with default settings reports **91 errors in 13 files**:

| Count | Kind | Cause |
|---:|---|---|
| 39 | `assignment` | Implicit Optional: `x: T = None`. PEP 484 removed this in 2018. |
| 36 | `arg-type` | `list[str \| tuple[str\|None,str]]` unions flow into functions that need only one half. |
| 7 | `return-value` | Wrong annotations (see below). |
| 6 | `str-unpack` | Same union problem. |
| 3 | `misc` | Tuple-length and comprehension typing. |

Specific problems:

- Implicit Optional (`= None` with a non-Optional type) is used in about 25 signatures. Write `T | None`.
- Wrong annotations:
  - `decisor.select` is annotated `-> list[list[float]]` but returns `list[float]`.
  - `converter.convert(maps: list[str])` should be `dict[str, str]`.
  - `guess` is annotated `-> str` but returns `None`.
  - `make_conll` returns bare `list`.
  - `scorer` stats tuples are annotated `tuple[int, int, int]`, but `tuple(map(sum, ...))` produces `tuple[int, ...]`.
- Bare `list`/`dict` appear in `guess`, `consolidate`, `compute_match_stats`, `read`, `save` and elsewhere.
- `**kwargs` is untyped (19 ANN003), and `kind`/`glue`/`otag` are forwarded blindly. This forwarding is the root cause of bugs #4 and #7.
- There is no `py.typed` marker, so downstream mypy treats the package as untyped even with hints.
- No mypy or ruff configuration exists.

Recommended fix:

1. Introduce aliases in one module (`econll/types.py`), for example `Tag`, `Pair = tuple[str | None, str]`, `Chunk`, `Span`, `Block`. Use `TypeAlias`, because PEP 695 `type` needs Python 3.12 and the project supports 3.10.
2. Use `@overload` for the polymorphic functions that take either tags or pairs and return the same kind: `chunk`, `remap`, `alter`, `rebase`, `convert`. That removes most of the 36 `arg-type` errors.
3. Take `Sequence` / `Mapping` for inputs and return concrete types.
4. Replace `**kwargs` forwarding with explicit keyword parameters or a small frozen `TagFormat` dataclass. This also fixes bugs #4 and #7 structurally.
5. Add `py.typed`, `Typing :: Typed`, and `[tool.mypy]` (strict on `src`).

## 3. Tests

Overall coverage is 73%, from 102 tests:

| Module | Coverage |
|---|---:|
| `__main__` | **0%** |
| `tabler` | 32% |
| `stats` | 38% |
| `scorer` | 71% (`tokeneval` and `chunkeval` are not exercised end to end) |
| `converter` | 86% |

- No test covers any bug above. `test_group_spans` uses pre-sorted input, which hides bug #6.
- Suggested additions:
  - CLI tests via `subprocess` or `main(argv)`
  - Golden-output tests for `report`
  - A `chunk`/`xcode` round-trip property test (the fuzz above is ready to adopt)
  - Regression tests for each item in section 1

## 4. Packaging / CI / hygiene

- `pyproject.toml`:
  - Add `[project.scripts] econll = "econll.__main__:main"`.
  - List classifiers for 3.10–3.13 (only 3.10 is listed now), plus `Typing :: Typed`.
  - Add `keywords`.
  - Add `[tool.pytest.ini_options]` (`testpaths`, coverage) and `[tool.ruff]` / `[tool.mypy]`.
  - `dev` could include `pytest-cov`, `mypy`, `ruff`.
- CI (copied from efusor): `actions/setup-python@v3` is old (use v5). The flake8 "warning" step runs with `--exit-zero`, so it never fails the build. Replace flake8 and pylint comments with ruff, and add a mypy step.
- `.gitignore`: add `.ruff_cache/`, and decide whether to track or ignore `uv.lock`.
- Docstrings are reST with `:type:` lines that duplicate the hints (ruff D finds 98 style issues: missing periods and summary spacing). Consider Google style without types.
- `docs/` (Sphinx, untracked) and `demo/evaluation.ipynb` were not audited for staleness.
- Positives:
  - pylint is 10/10 and flake8 is clean.
  - `strict=True` on `zip` is used consistently.
  - The module docstring function indexes are good.
  - The pure-function design is easy to test.

## 5. Suggested order of work

1. Fix reader bugs #1–#3 and `parse_tag`, and add regression tests.
2. Type pass: aliases, overloads, `T | None`, `py.typed`, mypy config. Replace `**kwargs` forwarding with `TagFormat`, which fixes #4 and #7.
3. `decisor` (#5, #6) and the empty-input crashes in `scorer` / `stats`.
4. `converter` and CLI hardening.
5. Replace `assert` with exceptions, warn on dropped chunks in `rebase`, and add CI mypy/ruff plus the coverage gaps.
