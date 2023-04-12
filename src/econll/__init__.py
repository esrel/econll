""" eCoNLL public functions """

__author__ = "Evgeny A. Stepanov"
__email__ = "stepanov.evgeny.a@gmail.com"
__status__ = "dev"
__version__ = "0.2.1"


from econll.reader import load, dump
from econll.parser import parse, merge, chunk, remap
from econll.xcoder import xcode
from econll.scorer import tokeneval, chunkeval
from econll.tabler import report
from econll.indexer import index
from econll.aligner import align, xbase
from econll.rebaser import rebase
from econll.schemer import guess, alter
from econll.decisor import decide, select, rerank, consolidate


__all__ = [
    # reader
    'load', 'dump',
    # parser
    'parse', 'merge', 'chunk', 'remap',
    # scorer
    'tokeneval', 'chunkeval',
    # tabler
    'report',
    # indexer
    'index',
    # aligner
    'align', 'xbase',
    # rebaser
    'rebase',
    # decisor
    'decide', 'select', 'rerank', 'consolidate',
    # schemer
    'guess', 'alter',
    # xcoder
    'xcode'
]
