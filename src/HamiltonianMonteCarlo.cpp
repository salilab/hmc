/**
 *  \file HamiltonianMonteCarlo.cpp
 *  \brief The Hamiltonian Monte Carlo algorithm
 *
 *  Copyright 2007-2018 IMP Inventors. All rights reserved.
 *
 */

#include <IMP/hmc/HamiltonianMonteCarlo.h>

IMPHMC_BEGIN_NAMESPACE

HamiltonianMonteCarlo::HamiltonianMonteCarlo(
  Model *m, Float kT, unsigned steps, Float timestep,unsigned persistence)
    : MonteCarlo(m) {

  mv_ = new MolecularDynamicsMover(m, steps, timestep);
  add_mover(mv_);
  md_ = mv_->get_md();
  set_kt(kT);
  set_number_of_md_steps(steps);
  set_timestep(timestep);
  set_persistence(persistence);
  set_return_best(false);
  persistence_counter_ = 0;
}

double HamiltonianMonteCarlo::do_evaluate(const ParticleIndexes &) const {
  if (get_use_incremental_scoring_function())
    IMP_THROW("Incremental scoring not supported", ModelException);
  double ekin = md_->get_kinetic_energy();
  double epot = get_scoring_function()->evaluate(false);
  return ekin + epot;
}

void HamiltonianMonteCarlo::do_step() {
  // gibbs sampler on x and v
  // persistence=p : sample p times x and once v
  // However because it's constant E, a rejected move
  // will result in recalculating the same move up to p times
  // until it is either accepted or the velocities are redrawn
  // since p has to be independent of the outcome (markov property)
  // we avoid recalculating the trajectory on rejection by just trying
  // it over and over without doing the md again.
  persistence_counter_ += 1;
  if (persistence_counter_ == persistence_) {
    persistence_counter_ = 0;
    // boltzmann constant in kcal/mol
    static const double kB = 8.31441 / 4186.6;
    md_->assign_velocities(get_kt() / kB);
  }
  ParticleIndexes unused;
  double last = do_evaluate(unused);
  core::MonteCarloMoverResult moved = do_move();

  double energy = do_evaluate(unused);
  bool accepted =
      do_accept_or_reject_move(energy, last, moved.get_proposal_ratio());
  while ((!accepted) && (persistence_counter_ < persistence_ - 1)) {
    persistence_counter_ += 1;
    accepted =
        do_accept_or_reject_move(energy, last, moved.get_proposal_ratio());
  }

  /*std::cout << "hmc"
      << " old " << last
      << " new " << energy
      << " delta " << energy-last
      << " accepted " << accepted
      <<std::endl;*/
}

Float HamiltonianMonteCarlo::get_kinetic_energy() const {
  return md_->get_kinetic_energy();
}

Float HamiltonianMonteCarlo::get_potential_energy() const {
  return get_scoring_function()->evaluate(false);
}

Float HamiltonianMonteCarlo::get_total_energy() const {
  return get_kinetic_energy() + get_potential_energy();
}

// set md timestep
void HamiltonianMonteCarlo::set_timestep(Float ts) {
  md_->set_maximum_time_step(ts);
}

double HamiltonianMonteCarlo::get_timestep() const {
  return md_->get_maximum_time_step();
}

// set number of md steps per mc step
void HamiltonianMonteCarlo::set_number_of_md_steps(unsigned nsteps) {
  mv_->set_number_of_md_steps(nsteps);
}

unsigned HamiltonianMonteCarlo::get_number_of_md_steps() const {
  return mv_->get_number_of_md_steps();
}

// set how many mc steps happen until you redraw the momenta
void HamiltonianMonteCarlo::set_persistence(unsigned persistence) {
  persistence_ = persistence;
}

unsigned HamiltonianMonteCarlo::get_persistence() const {
  return persistence_;
}

// return pointer to hmc::MolecularDynamics instance
// useful if you want to set other stuff that is not exposed here
MolecularDynamics *HamiltonianMonteCarlo::get_md() const { return md_; }

IMPHMC_END_NAMESPACE
