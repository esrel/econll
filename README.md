# eCoNLL: Extended CoNLL Evaluation for Shallow Parsing

## Installation

```commandline
pip install econll
```

## Command-Line Usage

### Correction

```commandline
python -m econll correct -i IFILE -o OFILE
```

### Conversion

```commandline
python -m econll convert -i IFILE -o OFILE -s TARGET_SCHEME
```

### Evaluation

```commandline
python -m econll evaluate -i IFILE
python -m econll evaluate -i IFILE -r REFS 
```

assumes that references and hypotheses are in the same file

#### Compatibility with `scikit-learn`'s `classification_report`

#### Compatibility with `conlleval.pl`

`conlleval.pl -d "\t" < data_file` output:

```
processed 50 tokens with 15 phrases; found: 14 phrases; correct: 7.
accuracy:  80.00%; precision:  50.00%; recall:  46.67%; FB1:  48.28
                X: precision:  37.50%; recall:  30.00%; FB1:  33.33  8
                Y: precision:  66.67%; recall:  80.00%; FB1:  72.73  6
```

`% econll evaluate -i data_file` output:

```

 Token Accuracy : 0.8000 
 Block Accuracy : 0.3000 
 Token Accuracy : 0.8200  (corrected)    
 Block Accuracy : 0.4000  (corrected)    

            Token-Level Evaluation            

 Label         P       R       F       S    

 B-X         0.8750  0.7000  0.7778      10 
 B-Y         0.7500  0.6000  0.6667       5 
 I-X         0.6000  0.5000  0.5455       6 
 I-Y         0.6667  1.0000  0.8000       4 
 O           0.8519  0.9200  0.8846      25 

 macro       0.7487  0.7440  0.7349      50 
 micro       0.8000  0.8000  0.8000      50 
 weighted    0.8013  0.8000  0.7940      50 


            Chunk-Level Evaluation            

 Label         P       R       F       S    

 X           0.3750  0.3000  0.3333      10 
 Y           0.6667  0.8000  0.7273       5 

 macro       0.5208  0.5500  0.5303      15 
 micro       0.5000  0.4667  0.4828      15 
 weighted    0.4722  0.4667  0.4646      15 

```



## Command-Line Arguments

```
(dev) eas@vui.com:~/Documents/MyDev/GitHub/econll % python src/econll/__main__.py -h
usage: PROG [-h] -i IPATH [-o OPATH] [-s {IO,IOB,IOBE,IOBES}] [-m MAPPING] [-r REFS] [--separator SEPARATOR] [--boundary BOUNDARY] [--docstart DOCSTART]
            [--kind {prefix,suffix}] [--glue GLUE] [--otag OTAG] [--digits DIGITS] [--style {md}]
            {evaluate,correct,convert}

CoNLL Sequence Labeling Evaluation

positional arguments:
  {evaluate,correct,convert}

options:
  -h, --help            show this help message and exit

I/O Arguments:
  -i IPATH, --ipath IPATH
                        path to data/hypothesis file
  -o OPATH, --opath OPATH
                        path to output file
  -s {IO,IOB,IOBE,IOBES}, --scheme {IO,IOB,IOBE,IOBES}
                        target scheme for conversion
  -m MAPPING, --mapping MAPPING
                        path to affix mapping file
  -r REFS, --refs REFS  path to references file

Data Format Arguments:
  --separator SEPARATOR
                        field separator string
  --boundary BOUNDARY   block separator string
  --docstart DOCSTART   doc start string

Tag Format Arguments:
  --kind {prefix,suffix}
                        IOB tag order
  --glue GLUE           IOB tag separator
  --otag OTAG           Out-of-Chunk IOB tag

Output Format Arguments:
  --digits DIGITS       output precision (decimal points)
  --style {md}          report table style

```