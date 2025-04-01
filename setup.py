#!/usr/bin/env python3
"""
Setup script for AFP Tools.
"""

from setuptools import setup, find_packages
import os

# Read the version from __init__.py
with open(os.path.join('afptools', '__init__.py'), 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip("'").strip('"')
            break
    else:
        version = '0.1.0'

# Read the long description from README.md
try:
    with open('README.md', 'r') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = 'AFP Tools - Utilities for working with AFP files'

setup(
    name='afptools',
    version=version,
    description='Utilities for working with AFP (Advanced Function Presentation) files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='AFP Tools Developer',
    author_email='user@example.com',
    url='https://github.com/user/afptools',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'afptools=afptools.cli:main',
        ],
    },
)
