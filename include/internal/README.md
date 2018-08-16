Place the private header files in this directory. They will be
available to your code with

     #include <IMP/hmc/internal/myheader.h>

All headers should include `IMP/hmc/hmc_config.h` as their
first include and surround all code with `IMPHMC_BEGIN_INTERNAL_NAMESPACE`
and `IMPHMC_END_INTERNAL_NAMESPACE` to put it in the
IMP::hmc::internal namespace and manage compiler warnings.
