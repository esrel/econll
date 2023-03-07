""" eCoNLL chunker tests """

from econll.chunker import chunk


def test_chunk(data_tags: list[list[str]],
               data_chunks: list[list[tuple[str, int, int]]]
               ) -> None:
    """
    test chunk
    :param data_tags: tag test cases
    :type data_tags: list[list[str]]
    :param data_chunks: reference chunks
    :type data_chunks: list[list[tuple[str, int, int]]]
    """
    for tags, chunks in zip(data_tags, data_chunks):
        assert chunks == chunk(tags)
