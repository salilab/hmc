/**
 *  \file IMP/hmc/MolecularDynamics.h
 *  \brief Simple molecular dynamics optimizer.
 *
 *  Copyright 2007-2018 IMP Inventors. All rights reserved.
 *
 */

#ifndef IMPHMC_MOLECULAR_DYNAMICS_H
#define IMPHMC_MOLECULAR_DYNAMICS_H

#include <IMP/hmc/hmc_config.h>
#include <IMP/Particle.h>
#include <IMP/Optimizer.h>
#include <IMP/atom/MolecularDynamics.h>
#include <IMP/isd/Nuisance.h>

IMPHMC_BEGIN_NAMESPACE

//! Molecular dynamics optimizer on 1-D and 3-D particles
/** The particles to be optimized must be XYZs or Nuisances, and should have a
 * non-optimizable mass.
 * \see atom::MolecularDynamics for more details
 */
class IMPHMCEXPORT MolecularDynamics : public atom::MolecularDynamics {
 public:
  /** Score based on the provided model */
  MolecularDynamics(Model *m = nullptr);

  //! Return the current kinetic energy of the system, in kcal/mol
  Float get_kinetic_energy() const;

  //! Assign velocities representative of the given temperature
  void assign_velocities(Float temperature);

 protected:
  bool get_is_simulation_particle(ParticleIndex pi) const;

  void setup_degrees_of_freedom(const ParticleIndexes &ps);

  //! First part of velocity Verlet (update coordinates and half-step velocity)
  void propagate_coordinates(const ParticleIndexes &ps,
                             double step_size);

  //! Second part of velocity Verlet (update velocity)
  void propagate_velocities(const ParticleIndexes &ps,
                            double step_size);

  //! Keys of the xyz velocities
  FloatKey vnuis_;
};

IMPHMC_END_NAMESPACE

#endif /* IMPHMC_MOLECULAR_DYNAMICS_H */
