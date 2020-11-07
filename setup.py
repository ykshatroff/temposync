#!/usr/bin/env python
# -*- coding: utf-8 -*-

import temposync

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = temposync.__version__

readme = open('README.md').read()
requirements = open('requirements.txt').readlines()

setup(
    name='temposync',
    version=version,
    description="""Sync work logs to Jira Tempo.""",
    long_description=readme,
    long_description_content_type='text/markdown',
    author='github.com/ykshatroff',
    author_email='ykshatroff@github.com',
    url='https://github.com/ykshatroff/temposync',
    packages=[
        'temposync',
    ],
    entry_points={
        'console_scripts': [
            'temposync = temposync.load_csv:load_csv',
        ],
    },
    include_package_data=True,
    install_requires=[line for line in requirements if line and not line.startswith(('#', '-'))],
    license="The Unlicense",
    keywords='jira tempo',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
