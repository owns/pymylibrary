#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages

def readme():
    with open("./README.md", mode="r", encoding="utf-8") as r:
        return r.read()

setup(
    name='PyMyLibrary',
    version='0.1.0',
    author='owns',
    author_email='owns13927@yahoo.com',

    keywords='python3 video movie manage',

    description='program for managing my library',
    long_description=readme(),
    long_description_content_type="text/markdown",
    #url='http://pypi.python.org/pypi/PyMyLibrary/',
    # license='LICENSE.txt',
    packages=find_packages(include=('pymylibrary',),exclude=('tests',)),

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        "Programming Language :: Python :: 3",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Operating System :: Microsoft", #OS Independent
    ],

    test_suite="pymylibrary.tests", #https://setuptools.readthedocs.io/en/latest/setuptools.html#test-build-package-and-run-a-unittest-suite

    #install_requires=[],
    # Include additional files into the package
    package_data={'pymylibrary': ['resources/MediaInfo.dll']},
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': ['PyMyLibrary=pymylibrary.__main__:main']
    }
)
