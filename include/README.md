Place the public header files in this directory. They will be
available to your code (and other modules) with

     #include <IMP/hmc/myheader.h>

All headers should include `IMP/hmc/hmc_config.h` as their
first include and surround all code with `IMPHMC_BEGIN_NAMESPACE`
and `IMPHMC_END_NAMESPACE` to put it in the IMP::hmc namespace
and manage compiler warnings.

Headers should also be exposed to SWIG in the `pyext/swig.i-in` file.
