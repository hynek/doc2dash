from setuptools import setup, find_packages

import codecs
import os
import re


here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r', 'utf-8') as f:
        return f.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='doc2dash',
    version=find_version('doc2dash', '__init__.py'),
    description="Convert docs to Dash.app's docset format.",
    long_description=open('README.rst').read(),
    url='http://github.com/hynek/doc2dash/',
    license='MIT',
    author='Hynek Schlawack',
    author_email='hs@ox.cx',
    packages=find_packages(exclude=['tests*']),
    entry_points={
        'console_scripts': [
            'doc2dash = doc2dash.__main__:main',
        ],
    },
    install_requires=open('requirements.txt').read().splitlines(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Documentation',
        'Topic :: Software Development',
        'Topic :: Software Development :: Documentation',
        'Topic :: Text Processing',
    ],
)
