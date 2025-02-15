#!/usr/bin/env python
from setuptools import setup, Extension
import re
import os


def read_file(filename, encoding='utf-8'):
    with open(filename, 'r', encoding=encoding) as f:
        return f.read()


def get_version():
    """
    Extract the version number from disjointset.c.
    It looks for a line of the form:
        #define DISJOINTSET_VERSION "x.y.z"
    """
    with open('disjointset.c', 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'#define\s+DISJOINTSET_VERSION\s+"([^"]+)"', content)
    if match:
        return match.group(1)
    raise RuntimeError('Unable to find version string in disjointset.c.')


here = os.path.abspath(os.path.dirname(__file__))

setup(
    name='disjointset',
    version=get_version(),
    description='Lightweight C extension module for Python that implements a disjoint set data type.',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    author='Grant Jenks',
    author_email='grant.jenks@gmail.com',
    url='https://github.com/grantjenks/python-disjointset',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: C',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    ext_modules=[Extension('disjointset', sources=['disjointset.c'])],
    python_requires='>=3.8',
)
