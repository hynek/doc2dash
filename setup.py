from setuptools import setup

import doc2dash


setup(
    name='doc2dash',
    version=doc2dash.__version__,
    description=doc2dash.__doc__.strip(),
    long_description=open('README.rst').read(),
    url='http://github.com/hynek/doc2dash/',
    license=doc2dash.__license__,
    author=doc2dash.__author__,
    author_email='hs@ox.cx',
    packages=[
        'doc2dash',
        'doc2dash.parsers',
    ],
    entry_points={
        'console_scripts': [
            'doc2dash = doc2dash.main:main',
        ],
    },
    install_requires=[
        'beautifulsoup4==4.1.0',
        'lxml==2.3.4',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
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
