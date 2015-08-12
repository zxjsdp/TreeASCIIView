from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='TreeASCIIView',
    version='0.2.5',
    description=('Provide a user friendly GUI for viewing Phylogenetic trees'
                 ' in ASCII style, based on jeetsukumaran/DendroPy. '),
    author='Haofei Jin',
    author_email='zxjsdp@gmail.com',
    url='https://github.com/zxjsdp/TreeASCIIView',
    license='Apache',
    keywords='tree phylogenetic ascii gui newick',
    packages=['asciitree'],
    install_requires=['dendropy'],
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['pytest', 'tox', 'sphinx'],
        'test': ['pytest'],
    },
    long_description=long_description,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
