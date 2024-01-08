from setuptools import setup, find_packages

import os


def read(path):
    return open(os.path.join(os.path.dirname(__file__), path)).read()


setup(
    name='econll',
    url='https://github.com/esrel/econll',
    version='0.2.2',
    author='Evgeny A. Stepanov',
    author_email='stepanov.evgeny.a@gmail.com',
    description='Extended CoNLL Utilities for Shallow Parsing',
    readme="README.md",
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    package_dir={'': "src"},
    packages=find_packages('src'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Intended Audience :: Science/Research',
    ],
    python_requires='>=3.10'
)
