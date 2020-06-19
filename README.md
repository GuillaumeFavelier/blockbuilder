[![PyPi](https://img.shields.io/pypi/v/blockbuilder?color=%231bcc1b)](https://pypi.org/project/blockbuilder/)
[![code style](https://img.shields.io/badge/code%20style-PEP8-green)](https://www.python.org/dev/peps/pep-0008/)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/2b132b99d65b4b358148b8284cdbf184)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=GuillaumeFavelier/blockbuilder&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/2b132b99d65b4b358148b8284cdbf184)](https://www.codacy.com?utm_source=github.com&utm_medium=referral&utm_content=GuillaumeFavelier/blockbuilder&utm_campaign=Badge_Coverage)
[![codecov](https://codecov.io/gh/GuillaumeFavelier/blockbuilder/branch/master/graph/badge.svg?token=AjF30DFi0b)](https://codecov.io/gh/GuillaumeFavelier/blockbuilder)
[![Maintenance](https://github.com/GuillaumeFavelier/blockbuilder/workflows/Maintenance/badge.svg)](https://github.com/GuillaumeFavelier/blockbuilder/actions?query=workflow%3AMaintenance)
[![Windows](https://github.com/GuillaumeFavelier/blockbuilder/workflows/Windows/badge.svg)](https://github.com/GuillaumeFavelier/blockbuilder/actions?query=workflow%3AWindows)
[![Linux](https://github.com/GuillaumeFavelier/blockbuilder/workflows/Linux/badge.svg)](https://github.com/GuillaumeFavelier/blockbuilder/actions?query=workflow%3ALinux)
[![MacOS](https://github.com/GuillaumeFavelier/blockbuilder/workflows/MacOS/badge.svg)](https://github.com/GuillaumeFavelier/blockbuilder/actions?query=workflow%3AMacOS)

![logo](https://raw.githubusercontent.com/GuillaumeFavelier/blockbuilder/master/logo/logo.png)

### BlockBuilder

*BlockBuilder* is an open-source Python application to build, edit and visualize
user-created sets of blocks (or voxels). The software is lightweight and highly
configurable and there is a particular emphasis on robustness and performance.
The user interface is built to be modern, minimalist and intuitive.

### Installation

To install the latest stable version of BlockBuilder, you can use `pip` in a terminal:

```sh
pip install -U blockbuilder
```

To create an environment with BlockBuilder installed, you can use `conda` in a terminal:

```sh
conda env create -f environment.yml
```

This should create a new environment called `blockbuilder`.

Although both `PyQt5` and `PySide2` are supported, BlockBuilder does not install
Python bindings for Qt by default. At least one of these two packages should be installed
but this choice is made by the user. Take a look at the [dependencies section](#dependencies)
to see the tested versions.

### Get the latest code

The latest changes are [available here](changelog/latest.md).

To install the latest version of the code using `pip`, open a terminal and type:

```sh
pip install -U https://github.com/GuillaumeFavelier/blockbuilder/archive/master.zip
```

To get the latest code using `git`, open a terminal and type:

```sh
git clone git://github.com/GuillaumeFavelier/blockbuilder.git
```

### Usage

To launch BlockBuilder once it is installed, it is as easy as using:

```sh
blockbuilder
```

Or from the source code using the standard starting script:

```sh
script/blockbuilder
```

![demo](https://raw.githubusercontent.com/GuillaumeFavelier/blockbuilder/master/demo.gif)

More details about the features are available in the [Wiki](https://github.com/GuillaumeFavelier/blockbuilder/wiki).

### Dependencies

The minimum required [dependencies](requirements.txt) to run BlockBuilder are:

-   numpy>=1.18.5
-   vtk>=8.1.2
-   qtpy>=1.9.0
-   PyQt5>=5.14.2 or PySide2>=5.14.2

### Resources

Many of the icons used in this project come from [material.io](https://material.io/resources/icons/?style=outline)

### Licensing

BlockBuilder is [BSD-licenced (3 clause)](LICENSE):

```txt
BSD 3-Clause License

Copyright (c) 2020, Guillaume Favelier
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```
