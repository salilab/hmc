\brief Hamiltonian Monte Carlo for Integrative Modeling

This module provides functionality for using Dynamic/Adaptive Hamiltonian
Monte Carlo (HMC) to sample IMP Models. This interface is experimental and
can change at any time.

## Installing Dependencies

The package currently has several dependencies in the Julia language. Follow
the following steps to install `IMP.hmc`'s dependencies:

1. Install [Julia](https://julialang.org/downloads/)

2. Install the [HMCUtilities.jl](https://github.com/salilab/HMCUtilities.jl)
package from the command line with

```bash
julia -e 'using Pkg; Pkg.add("https://github.com/salilab/HMCUtilities.jl")'
```

3. Install the Python/Julia interface with

```bash
$ pip install pyjulia
$ python
>>> import julia
>>> julia.install()
```

Then install this module using the standard approach.

## Examples

See [`examples/notebooks`](examples/notebooks) for example usage.

# Info

_Author(s)_: Seth Axen

_Maintainer_: `sdaxen`

_License_: [LGPL](http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html)
This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2 of the License, or (at your option) any later version.

_Publications_:
- None
