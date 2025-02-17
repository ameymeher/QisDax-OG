# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import inspect
import os
import setuptools
import sys

requirements = [
]


if not hasattr(setuptools,
               'find_namespace_packages') or not inspect.ismethod(
        setuptools.find_namespace_packages):
    print("Your setuptools version:'{}' does not support PEP 420 "
          "(find_namespace_packages). Upgrade it to version >='40.1.0' and "
          "repeat install.".format(setuptools.__version__))
    sys.exit(1)

version_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'qiskit', 'providers', 'dax',
                 'VERSION.txt'))


with open(version_path, 'r') as fd:
    version = fd.read().rstrip()

README_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           'README.md')
with open(README_PATH) as readme_file:
    README = readme_file.read()


setuptools.setup(
    name="qiskit-dax-provider",
    version=version,
    description="Qiskit provider for ARTIQ backends",
    long_description=README,
    long_description_content_type='text/markdown',
    author="Alexander Allen, Keith Mellendorph",
    author_email="arallen4@ncsu.edu, kmellen@ncsu.edu",
    license="Apache 2.0",
    classifiers=[
        "Environment :: Console",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering",
    ],
    keywords="qiskit sdk quantum",
    packages=setuptools.find_namespace_packages(exclude=['test*']),
    install_requires=requirements,
    include_package_data=True,
    python_requires=">=3.5, <3.10",
    zip_safe=False
)
