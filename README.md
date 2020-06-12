[![Codacy Badge](https://app.codacy.com/project/badge/Grade/2b132b99d65b4b358148b8284cdbf184)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=GuillaumeFavelier/blockbuilder&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/2b132b99d65b4b358148b8284cdbf184)](https://www.codacy.com?utm_source=github.com&utm_medium=referral&utm_content=GuillaumeFavelier/blockbuilder&utm_campaign=Badge_Coverage)
[![codecov](https://codecov.io/gh/GuillaumeFavelier/blockbuilder/branch/master/graph/badge.svg?token=AjF30DFi0b)](https://codecov.io/gh/GuillaumeFavelier/blockbuilder)
[![Build Status](https://dev.azure.com/guillaumefavelier/blockbuilder/_apis/build/status/GuillaumeFavelier.blockbuilder?branchName=master)](https://dev.azure.com/guillaumefavelier/blockbuilder/_build/latest?definitionId=2&branchName=master)
![Testing](https://github.com/GuillaumeFavelier/blockbuilder/workflows/Testing/badge.svg)

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

![screenshot](https://raw.githubusercontent.com/GuillaumeFavelier/blockbuilder/master/screenshot.png)

More details about the features will be available soon in the wiki.

### Dependencies

The minimum required [dependencies](requirements.txt) to run BlockBuilder are:

-   numpy>=1.18.5
-   vtk>=8.1.2
-   PyQt5>=5.15.0

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
