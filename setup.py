from setuptools import setup, find_packages
from os import path
from codecs import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name="TrawlAgent",
    version="0.2.2",
    author="Matt Iavarone",
    author_email="matt.iavarone@gmail.com",
    packages=find_packages(),
    long_description  = long_description,
    url = 'https://trawl.io',
    license = 'TBD',
    classifiers = [
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    keywords = 'trawl trawler trawl_agent trawlers logs',
    package_data = {'': ['trawl', 'trawl.cfg']},
    data_files = [('/usr/bin/', ['trawl']), ('/etc/sysconfig/trawl', ['trawl_agent/conf/trawl.yaml']), ('/lib/systemd/system/', ['trawl.service']), ('/etc/rsyslog.d/', ['22-trawl.conf'])],
    install_requires = ['requests>=2.5.1', 'psutil>=2.2.1'],

)
