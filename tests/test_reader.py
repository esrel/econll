import string

from econll.reader import Token, load, save, read, split, merge


def gen_dummy_tokens(data: list[list[str]]) -> list[list[str]]:
    char_list = [*string.ascii_lowercase]
    return [char_list[:len(seq)] for seq in data]


def test_io(conll_refs, conll_hyps):
    data = merge(gen_dummy_tokens(conll_refs), conll_refs, conll_hyps)
    path = "/tmp/conll.txt"

    save(data, path)

    read_data = read(path)

    assert data == read_data

    refs, hyps = split(read_data)

    assert refs == conll_refs
    assert hyps == conll_hyps

    # load_data = load(read_data)

    # print(refs)
    # print(hyps)

