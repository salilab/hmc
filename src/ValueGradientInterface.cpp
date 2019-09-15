/**
 *  \file ValueGradientInterface.h
 *  \brief Utility for setting/getting values and getting the gradient
 *
 *  Copyright 2007-2019 IMP Inventors. All rights reserved.
 *
 */

#include <IMP/hmc/ValueGradientInterface.h>

IMPHMC_BEGIN_NAMESPACE

ValueGradientInterface::ValueGradientInterface(IMP::Model *m,
                                               const IMP::FloatKeys& fks,
                                               const IMP::ParticleIndexes& pis,
                                               std::string name)
  : IMP::ModelObject(m, name), fks_(fks), pis_(pis), x_(pis.size()), gradx_(pis.size()) {
    IMP_USAGE_CHECK(pis.size() == fks.size(),
                    "Number of particle indexes and float keys must be equal.");
}

int ValueGradientInterface::get_dimension() const { return x_.size(); }

IMP::FloatKeys ValueGradientInterface::get_float_keys() const { return fks_; }

IMP::ParticleIndexes ValueGradientInterface::get_particle_indexes() const { return pis_; }

IMP::Vector<double> ValueGradientInterface::get_values() const {
  for (int i = 0; i < get_dimension(); ++i)
    x_[i] = get_model()->get_attribute(fks_[i], pis_[i]);
  return x_;
}

void ValueGradientInterface::set_values(const IMP::Vector<double> &x) {
  IMP_USAGE_CHECK(x.size() == x_.size(),
                  "Position vector must be same length as particle indexes.");
  for (int i = 0; i < get_dimension(); ++i)
    get_model()->set_attribute(fks_[i], pis_[i], x[i]);
}

IMP::Vector<double> ValueGradientInterface::get_gradient() const {
  for (int i = 0; i < get_dimension(); ++i)
    gradx_[i] = get_model()->get_derivative(fks_[i], pis_[i]);
  return gradx_;
}

IMP::ModelObjectsTemp ValueGradientInterface::do_get_inputs() const {
  IMP::ParticlesTemp ret;
  for (int i = 0; i < get_dimension(); ++i)
    ret.push_back(get_model()->get_particle(pis_[i]));
  return ret;
}

IMP::ModelObjectsTemp ValueGradientInterface::do_get_outputs() const {
  return IMP::ParticlesTemp(0);
}

IMPHMC_END_NAMESPACE
