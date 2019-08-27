# If numba is imported, it must be before Julia
# see https://github.com/JuliaPy/pyjulia/issues/307
try:
    import numba
except ImportError:
    pass

import julia
from julia import Main
from julia import Base
import julia.HMCUtilities
from julia import HMCUtilities
import julia.HMCUtilities.AdvancedHMC
from julia.HMCUtilities import AdvancedHMC

Main.eval("using HMCUtilities")
