/**
 *  \file IMP/hmc/HamiltonianMonteCarlo.h
 *  \brief A Hamiltonian Monte Carlo implementation
 *
 *  Copyright 2007-2018 IMP Inventors. All rights reserved.
 *
 */

#ifndef IMPHMC_HAMILTONIAN_MONTE_CARLO_H
#define IMPHMC_HAMILTONIAN_MONTE_CARLO_H

#include <IMP/hmc/hmc_config.h>
#include <IMP/core/MonteCarlo.h>
#include <IMP/hmc/MolecularDynamics.h>
#include <IMP/hmc/MolecularDynamicsMover.h>
#include <IMP/macros.h>

IMPHMC_BEGIN_NAMESPACE

//! Hamiltonian Monte Carlo optimizer
// moves all xyz particles having a fixed mass with an MD proposal

class IMPHMCEXPORT HamiltonianMonteCarlo : public core::MonteCarlo {

 public:
  HamiltonianMonteCarlo(Model *m, Float kT = 1.0, unsigned steps = 100,
                        Float timestep = 1.0, unsigned persistence = 1);

  Float get_kinetic_energy() const;

  Float get_potential_energy() const;

  Float get_total_energy() const;

  // set md timestep
  void set_timestep(Float ts);
  double get_timestep() const;

  // set number of md steps per mc step
  void set_number_of_md_steps(unsigned nsteps);
  unsigned get_number_of_md_steps() const;

  // set how many mc steps happen until you redraw the momenta
  void set_persistence(unsigned persistence = 1);
  unsigned get_persistence() const;

  // return pointer to hmc::MolecularDynamics instance
  // useful if you want to set other stuff that is not exposed here
  MolecularDynamics *get_md() const;

  // evaluate should return the total energy
  double do_evaluate(const ParticleIndexes &) const;

  virtual void do_step();
  IMP_OBJECT_METHODS(HamiltonianMonteCarlo);

 private:
  unsigned num_md_steps_, persistence_;
  unsigned persistence_counter_;
  IMP::PointerMember<MolecularDynamicsMover> mv_;
  Pointer<MolecularDynamics> md_;
};

IMPHMC_END_NAMESPACE

#endif /* IMPHMC_HAMILTONIAN_MONTE_CARLO_H */
