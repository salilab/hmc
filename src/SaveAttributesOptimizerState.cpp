/**
 *  \file SaveAttributesOptimizerState.cpp
 *  \brief Store attributes of the model.
 *
 *  Copyright 2007-2019 IMP Inventors. All rights reserved.
 *
 */

#include <IMP/hmc/SaveAttributesOptimizerState.h>

IMPHMC_BEGIN_NAMESPACE

SaveAttributesOptimizerState::SaveAttributesOptimizerState(
    ValueGradientInterface* interface)
    : OptimizerState(interface->get_model(), "SaveAttributesOptimizerState%1%"),
      interface_(interface) {}

void SaveAttributesOptimizerState::do_update(unsigned int) {
  const std::vector<double> vs = interface_->get_values();
  Floats ret(vs.size());
  for (unsigned int i = 0; i < vs.size(); ++i)
    ret[i] = vs[i];
  vs_.push_back(ret);
}

ValueGradientInterface* SaveAttributesOptimizerState::get_interface() {
  return interface_;
}

FloatsList SaveAttributesOptimizerState::get_values() const { return vs_; }

IMPHMC_END_NAMESPACE
