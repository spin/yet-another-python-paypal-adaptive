#!/usr/bin/env python

from setuptools import setup, find_packages
import yappa

REQUIREMENTS = [
    'requests==2.10.0',
    'pytz==2016.4'
]

setup(
    name='yappa',
    version=".".join(map(str, yappa.__version__)),
    author='Spin Lai',
    author_email='pengo.lai@gmail.com',
    install_requires=REQUIREMENTS,
    description='Another Python library for integrating PayPal Adaptive Payments',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite='nose.collector',
    tests_require=[
        'nose'
    ],
)
