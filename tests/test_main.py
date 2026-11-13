""" eCoNLL command-line interface tests """

import json

import pytest

from econll.__main__ import main, read, save
from econll.reader import dump, load


@pytest.fixture(name="conll_path")
def fixture_conll_path(tmp_path) -> str:
    """ CoNLL file: token, reference, hypothesis """
    path = tmp_path / "data.tsv"
    dump([[("aaa", "B-X", "B-X"), ("bbb", "I-X", "O")], [("ccc", "O", "O")]], str(path))
    return str(path)


def test_eval(conll_path: str, capsys: pytest.CaptureFixture[str]) -> None:
    """ test `eval` command """
    main(["eval", "-d", conll_path])
    out = capsys.readouterr().out

    assert "Token-Level Evaluation" in out
    assert "Chunk-Level Evaluation" in out


def test_stat(conll_path: str, capsys: pytest.CaptureFixture[str]) -> None:
    """ test `stat` command """
    main(["stat", "-d", conll_path])
    out = capsys.readouterr().out

    assert "block count: 2" in out
    assert "chunk-level stats" in out


def test_conv(conll_path: str, tmp_path) -> None:
    """ test `conv` command: conll -> mdown -> parse (jsonl) -> conll """
    mdown, jsonl, conll = (str(tmp_path / name) for name in ("o.mdown", "o.jsonl", "o.tsv"))

    main(["conv", "-d", conll_path, "-f", "mdown", "-o", mdown])
    # the last column (hypothesis) is the tag
    assert read(mdown) == ["[aaa](X) bbb", "ccc"]

    main(["conv", "-d", mdown, "-f", "parse", "-o", jsonl])
    assert [item["text"] for item in read(jsonl)] == ["aaa bbb", "ccc"]

    main(["conv", "-d", jsonl, "-f", "conll", "-o", conll])
    assert load(conll) == [[("aaa", "B-X"), ("bbb", "O")], [("ccc", "O")]]


def test_conv_tag_format(conll_path: str, tmp_path) -> None:
    """ test `conv` command: tag format params are respected """
    mdown = str(tmp_path / "o.mdown")
    path = tmp_path / "suffix.tsv"
    dump([[("aaa", "X_B"), ("bbb", "X_I")]], str(path))

    main(["conv", "-d", str(path), "--kind", "suffix", "--glue", "_", "-f", "mdown", "-o", mdown])
    assert read(mdown) == ["[aaa bbb](X)"]


def test_conv_requires_outs(conll_path: str) -> None:
    """ test `conv` command: output path is required """
    with pytest.raises(SystemExit):
        main(["conv", "-d", conll_path, "-f", "mdown"])


def test_read_save(tmp_path) -> None:
    """ test read & save: empty lines are skipped; non-ASCII text is kept as is """
    path = tmp_path / "data.jsonl"
    save([{"text": "caffè"}], str(path))

    assert "caffè" in path.read_text(encoding="utf-8")
    assert read(str(path)) == [{"text": "caffè"}]

    path.write_text(json.dumps({"text": "a"}) + "\n\n", encoding="utf-8")
    assert read(str(path)) == [{"text": "a"}]
