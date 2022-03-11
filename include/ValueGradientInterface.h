/**
 *  \file IMP/hmc/ValueGradientInterface.h
 *  \brief Utility for setting/getting values and getting the gradient
 *
 *  Copyright 2007-2019 IMP Inventors. All rights reserved.
 *
 */

#ifndef IMPHMC_VALUE_GRADIENT_INTERFACE_H
#define IMPHMC_VALUE_GRADIENT_INTERFACE_H

#include <IMP/hmc/hmc_config.h>
#include <IMP/Particle.h>
#include <IMP/ModelObject.h>
#include <IMP/Model.h>
#include <IMP/Vector.h>

IMPHMC_BEGIN_NAMESPACE

//! Utility for setting/getting values and getting the gradient
class IMPHMCEXPORT ValueGradientInterface : public IMP::ModelObject {
 private:
  IMP::FloatKeys fks_;
  IMP::ParticleIndexes pis_;
  mutable IMP::Vector<double> x_;
  mutable IMP::Vector<double> gradx_;

 public:
  ValueGradientInterface(IMP::Model* m, const IMP::FloatKeys& fks,
                         const IMP::ParticleIndexes& pis,
                         std::string name = "ValueGradientInterface%1%");

  int get_dimension() const;

  IMP::FloatKeys get_float_keys() const;

  IMP::ParticleIndexes get_particle_indexes() const;

  IMP::Vector<double> get_values() const;

  void set_values(const IMP::Vector<double>& x);

  IMP::Vector<double> get_gradient() const;

  virtual IMP::ModelObjectsTemp do_get_inputs() const override;

  virtual IMP::ModelObjectsTemp do_get_outputs() const override;

 protected:
  IMP_OBJECT_METHODS(ValueGradientInterface);
};

IMP_OBJECTS(ValueGradientInterface, ValueGradientInterfaces);

IMPHMC_END_NAMESPACE

#endif /* IMPHMC_VALUE_GRADIENT_INTERFACE_H */
