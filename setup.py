from setuptools import setup, find_packages

import os


def read(path):
    return open(os.path.join(os.path.dirname(__file__), path)).read()


setup(
    name='econll',
    version='0.1.2',
    description='Extended CoNLL Sequence Labeling Evaluation Utilities',
    readme="README.md",
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    url='https://github.com/esrel/econll',
    author='Evgeny A. Stepanov',
    author_email='stepanov.evgeny.a@gmail.com',
    package_dir={'': "src"},
    packages=find_packages('src'),
    classifiers=['Development Status :: 2 - Pre-Alpha'],
)
