from setuptools import setup

from triq import (
    __version__,
    __description__,
    __url__,
    __author__,
    __author_email__,
    __keywords__
)

NAME = 'triq'

with open('requirements.txt') as f:
    install_requires = f.readlines()

setup(
    name=NAME,
    version=__version__,
    description=__description__,
    long_description='See ' + __url__,
    url=__url__,
    author=__author__,
    author_email=__author_email__,
    keywords=__keywords__,

    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=['triq'],
    install_requires=install_requires,
)
