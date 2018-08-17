/**
 *  \file IMP/hmc/MolecularDynamicsMover.h
 *  \brief A modifier which perturbs XYZs or Nuisances with a constant energy
 *  MD simulation.
 *
 *  Copyright 2007-2018 IMP Inventors. All rights reserved.
 *
 */

#ifndef IMPHMC_MOLECULAR_DYNAMICS_MOVER_H
#define IMPHMC_MOLECULAR_DYNAMICS_MOVER_H

#include <IMP/hmc/hmc_config.h>
#include <IMP/core/MonteCarloMover.h>
#include <IMP/hmc/MolecularDynamics.h>

IMPHMC_BEGIN_NAMESPACE

//! Modify a set of continuous variables using a MD simulation.
/** \see MonteCarlo
 */
class IMPHMCEXPORT MolecularDynamicsMover : public core::MonteCarloMover {
 public:
  MolecularDynamicsMover(Model *m, unsigned nsteps = 100,
                         Float timestep = 1.);

  MolecularDynamics *get_md() const { return md_; }

  unsigned get_number_of_md_steps() const { return nsteps_; }
  void set_number_of_md_steps(unsigned nsteps) {
    IMP_USAGE_CHECK(nsteps >= 1, "nsteps must be positive!");
    nsteps_ = nsteps;
  }

 protected:
  // mover-specific function calls
  virtual ModelObjectsTemp do_get_inputs() const IMP_OVERRIDE;
  virtual core::MonteCarloMoverResult do_propose() IMP_OVERRIDE;
  virtual void do_reject() IMP_OVERRIDE;
  IMP_OBJECT_METHODS(MolecularDynamicsMover);

 private:
  void save_coordinates();

  unsigned nsteps_;
  IMP::PointerMember<MolecularDynamics> md_;
  std::vector<std::vector<double> > coordinates_;
  std::vector<std::vector<double> > velocities_;
};

IMPHMC_END_NAMESPACE

#endif /* IMPHMC_MOLECULAR_DYNAMICS_MOVER_H */
