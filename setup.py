# SPDX-License-Identifier: MIT

import os
import setuptools


here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='jeepney-objects',
    version='0.0.1',
    description='Jeepney objects implementation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/libratbag/ratbag-emu',
    author='Filipe Laíns',
    author_email='lains@archlinux.org',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
    ],
    keywords='dbus jeepney',
    project_urls={
        'Bug Reports': 'https://github.com/FFY00/jeepney-objects/issues',
        'Source': 'https://github.com/FFY00/jeepney-objects',
    },

    packages=[
        'jeepney_objects',
        'jeepney_objects.integration',
    ],
    install_requires=['jeepney'],
    tests_require=[
        'pytest',
    ],
)
