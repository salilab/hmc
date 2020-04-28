\brief Hamiltonian Monte Carlo for Integrative Modeling

[![Build Status](https://travis-ci.org/salilab/hmc.svg?branch=master)](https://travis-ci.org/salilab/hmc)
[![codecov](https://codecov.io/gh/salilab/hmc/branch/master/graph/badge.svg)](https://codecov.io/gh/salilab/hmc)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/bcced071b3f541449d723a774ea09026)](https://www.codacy.com/app/salilab/hmc?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=salilab/hmc&amp;utm_campaign=Badge_Grade)

This module provides functionality for using Dynamic/Adaptive Hamiltonian
Monte Carlo (HMC) to sample IMP Models. This interface is experimental and
can change at any time.

## Installing Dependencies

The package currently has several dependencies in the Julia language. Follow
the following steps to install `IMP.hmc`'s dependencies:

1. Install [Julia](https://julialang.org/downloads/)

2. Install the Python/Julia interface with

```console
$ pip install julia
$ python -c 'import julia; julia.install()'
```

3. Install the [HMCUtilities.jl](https://github.com/salilab/HMCUtilities.jl)
package from the command line with

```console
$ julia -e 'using Pkg; Pkg.add(PackageSpec(url="https://github.com/salilab/HMCUtilities.jl", rev="v0.2.1"))'
```

Then install this module using the
[standard approach](https://integrativemodeling.org/nightly/doc/manual/outoftree.html).

For [some configurations](https://pyjulia.readthedocs.io/en/latest/troubleshooting.html),
you may need to use `python-jl` instead of `python`. The usage is identical.

## Examples

See [`examples/notebooks`](examples/notebooks) for example usage.

# Info

_Author(s)_: Seth Axen

_Maintainer_: `sethaxen`

_License_: [LGPL](http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html)
This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2 of the License, or (at your option) any later version.

_Publications_:
- None
