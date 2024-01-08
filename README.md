# eCoNLL: Extended CoNLL Utilities for Shallow Parsing

[![Supported Python Versions](https://img.shields.io/pypi/pyversions/econll.svg)](https://pypi.python.org/pypi/econll/)
[![PyPI version](https://img.shields.io/pypi/v/econll.svg)](https://pypi.org/project/econll/)
[![PyPI downloads](https://img.shields.io/pypi/dm/econll.svg)](https://pypistats.org/packages/econll/)

## Shallow Parsing

### Sequence Labeling and Classification

[Classification](https://en.wikipedia.org/wiki/Statistical_classification) 
is the problem of identifying to which of a set of categories (subpopulations) a new observation belongs, 
on the basis of a training set of data containing observations (or instances) whose category membership is known.

[Sequence Labeling](https://en.wikipedia.org/wiki/Sequence_labeling) 
is a type of pattern recognition task that involves the algorithmic assignment of a categorical label to each member 
of a sequence of observed values. 
It is a subclass of [structured (output) learning](https://en.wikipedia.org/wiki/Structured_prediction), 
since we are predicting a *sequence* object rather than a discrete or real value predicted in classification problems.

### Sequence Labeling and Shallow Parsing

[Shallow Parsing](https://en.wikipedia.org/wiki/Shallow_parsing) is a kind of Sequence Labeling. 
The main difference from Sequence Labeling task, 
such as [Part-of-Speech Tagging](https://en.wikipedia.org/wiki/Part-of-speech_tagging), 
where there is an output label (tag) per token; 
Shallow Parsing additionally performs __chunking__ -- segmentation of input sequence into constituents. 
Chunking is required to identify categories (or types) of *multi-word expressions*.

In other words, we want to be able to capture information that expressions like `"New York"` that consist of 2 tokens, 
constitute a single unit.

What this means in practice is that Shallow Parsing performs *jointly* (or not) 2 tasks:
- __Segmentation__ of input into constituents (__spans__)
- __Classification__ (Categorization, Labeling) of these constituents into predefined set of labels (__types__)

### CoNLL Corpus Format

Corpus in *CoNLL* format consists of series of sentences, separated by blank lines. 
Each sentence is encoded using a table (or "grid") of values, where each line corresponds to a single word, 
and each column corresponds to an annotation type (such as various token-level features & labels). 

The set of columns used by CoNLL-style files can vary from corpus to corpus.

Since a line in a data can correspond to any token (word or not), it is referred to by a more general term `token`.
Similarly, since a data can be composed of units more or less than a sentence, 
a new line separated unit is referred to as `block`.

### Encoding Segmentation Information

#### [IOB Scheme](https://en.wikipedia.org/wiki/Inside%E2%80%93outside%E2%80%93beginning_(tagging))

The notation scheme is used to label *multi-word* spans in token-per-line format, 
e.g. that *New York* is a *LOCATION* concept that has 2 tokens.

As such a token-level `tag` consists of an `affix` that encodes segmentation information 
and `label` that encodes type information.
Consequently, the corpus `tagset` consists of all possible `affix` and `label` combinations.

A segment encoded with `affix`es and assigned a `label` is referred to as `chunk`.
  
- Both, prefix and suffix notations are commons: 
    - prefix: __B-LOC__
    - suffix: __LOC-B__

- Meaning of Affixes
    - __I__ for Inside of span
    - __O__ for Outside of span (no prefix or suffix, just `O`)
    - __B__ for Beginning of span

#### Alternative Schemes

- No affix (useful when there are no multi-word concepts)
- `IO`: deficient without `B`
- `IOB`: see above
- `IOBE`: `E` for End of span (`L` in `BILOU` for Last)
- `IOBES`: `S` for Singleton (`U` in `BILOU` for Unit)

### Evaluation

There are several methods to evaluate performance of shallow parsing models. 
They can be evaluated at `token`-level and at `chunk`-level. 

#### Token-Level Evaluation

The unit of evaluation in this case is a `tag` of a `token`, 
and what is evaluated is how accurately a model assigns tags to tokens.
Consequently, the `token` (or `tag`) **accuracy** measures the amount of correctly predicted `tag`s. 

Since a `tag` consists of an `affix`-`label` pair, 
it is additionally possible to separately compute `affix` and `label` performances. 

#### Chunk-Level Evaluation

The unit of evaluation in this case is a `chunk`, and the evaluation is "joint"; 
in the sense that it jointly evaluates segmentation and labeling.
That is, a `true` unit is the one that has correct `label` and `span`.

Similar to token-level evaluation, it is possible to evaluate segmentation independently of labeling. 
This is achieved ignoring the `chunk` label, e.g. by converting all of them to a single label. 


## Why **eCoNLL**?

Token-level evaluation is readily available from a number of packages, 
and can be easily computed using `scikit-learn`'s `classification_report`, for instance.

Chunk-level evaluation was originally provided by 
`conlleval` [perl script](https://www.cnts.ua.ac.be/conll2000/chunking/conlleval.txt) within CoNLL Shared Tasks.
However, the one limitation of `conlleval` is that it does not support `IOBES` or `BILOU` schemes.

The `conlleval` script was ported to python numerous times, and these ports have various functionalities.
One notable port is [`seqeval`](https://github.com/chakki-works/seqeval), 
which is also included in Hugging Face's [`evaluate`](https://github.com/huggingface/evaluate) package.


## Installation

To install `econll` run:

```commandline
pip install econll
```

## Usage

It is possible to run `econll` from command-line, as well as to import the methods.

### Command-Line Usage

```
usage: PROG [-h] -d DATA [-r REFS] 
                         [--separator SEPARATOR] [--boundary BOUNDARY] [--docstart DOCSTART] 
                         [--kind {prefix,suffix}] [--glue GLUE] [--otag OTAG]

eCoNLL: Extended CoNLL Utilities

options:
  -h, --help            show this help message and exit

I/O Arguments:
  -d DATA, --data DATA  path to data/hypothesis file
  -r REFS, --refs REFS  path to references file

Data Format Arguments:
  --separator SEPARATOR
                        field separator string
  --boundary BOUNDARY   block separator string
  --docstart DOCSTART   doc start string

Tag Format Arguments:
  --kind {prefix,suffix}
                        tag order
  --glue GLUE           tag separator
  --otag OTAG           outside tag

```

#### Evaluation

```commandline
python -m econll evaluate -d DATA
python -m econll evaluate -d DATA -r REFS
```

## Versioning

This project adheres to [Semantic Versioning](https://semver.org/).



