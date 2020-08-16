#!/usr/bin/env python3
from distutils.core import setup

import setuptools

setup(
    name='rabbitholer',
    version='0.0.2',
    include_package_data=True,
    author='Stanislav Arnaudov',
    author_email='stanislv_ts@abv.bg',
    description='A simple tool to send and receive messages to and from rabbitmq\
exchanges and queues',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    license='GNU General Public License v3.0',
    keywords='rabbitmq sender receiver',
    url='https://github.com/palikar/rabbitholer',
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov'],
    entry_points={
        'console_scripts': [
            'rabbitholer = rabbitholer.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Console',
        'Topic :: System :: Logging',
        'Topic :: System :: Monitoring',
        'Topic :: Utilities',

    ],
)
