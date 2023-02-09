# Annotation Transfer

Due to the fact that different (pretrained) models, such as `spacy`, `transformers`, etc. 
make use of specific tokenizers; it is often the case that there arises a need to *align* the `target` predictions 
and *transfer* the predicted labels to the `source` (reference) tokens.

The `align_tokens` method serves this exact purpose. 
It computes the *alignment* between `source` and `target` tokens 
and *transfers* `target`'s `label` and `affix` attributes to the `source` token. 

## Token Normalization

Fundamentally, *tokenization* is the process of segmentation of input text into units of analysis (*tokens*). 
These units are possibly classified and replaced with some other tokens 
(e.g. `(` with `-LRB-` by Penn Treebank Tokenization). 
In case an input token (white space delimited unit of text) is split into several, 
some tokenizers (e.g. `WordPiece`) mark such units with a prefix (e.g. `##`).

Such tokenization allows to recover the text of the original by applying the operation in reverse. 
However, in case some portion of input text is removed (e.g. punctuation), 
or some of it is *normalized* to a common token (e.g. numeral to `<num>`), it is not.

For the *alignment* we assume that tokenization is recoverable.

## Alignment Computation

Since it is assumed that both `source` and `target` are tokens over the same text; 
the *alignment* is computed making use of *common* token span begin and end indices 
(`Token`'s `bos` and `eos` attributes, respectively).

## Transfer of Parameters

`['B-X', 'I-X']`