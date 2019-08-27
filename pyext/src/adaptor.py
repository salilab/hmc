from timeit import default_timer as timer

from .julia import AdvancedHMC


class Adaptor(object):

    """Adapt the step size and metric during warm-up.

    Currently just a thin wrapper for an `AdvancedHMC.StanHMCAdaptor`."""

    def __init__(self, hmc, nadapt=2000, adapt_delta=0.8):
        self.hmc = hmc
        self.create_adaptor(nadapt, adapt_delta=adapt_delta)

    @property
    def nadapt(self):
        return self.adaptor.n_adapts

    def is_adapting(self):
        return self.nadapt_counter < self.nadapt

    def create_adaptor(self, nadapt, adapt_delta=0.8):
        self.adaptor = AdvancedHMC.StanHMCAdaptor(
            nadapt,
            AdvancedHMC.Preconditioner(self.hmc.hamiltonian.metric),
            AdvancedHMC.NesterovDualAveraging(adapt_delta, self.hmc.step_size),
        )
        self.nadapt_counter = 0

    def adapt_step(self):
        AdvancedHMC.adapt_b(
            self.adaptor,
            self.hmc.phasepoint.θ,
            self.hmc.stats.current["accept_stat"],
        )
        self.hmc.hamiltonian.hamiltonian, self.hmc.sampler = AdvancedHMC.update(
            self.hmc.hamiltonian.hamiltonian, self.hmc.sampler, self.adaptor
        )
        self.nadapt_counter += 1

    def adapt(self, update_states=False, log_freq=0.01, verbose=True):
        print("Warming up HMC for {} steps.".format(self.nadapt))

        try:
            self.hmc.stats.clear()
        except AttributeError:
            pass

        try:
            self.hmc.samples.clear()
        except AttributeError:
            pass

        if verbose:
            log_interval = int(self.nadapt * log_freq)

        if not update_states:
            opt_states = self.hmc.get_optimizer_states()
            self.hmc.clear_optimizer_states()

        ndivergent = 0
        nevals = 0
        self.hmc.before_sample()
        start = timer()
        while self.is_adapting():
            self.hmc.sample()
            self.adapt_step()
            ndivergent += self.hmc.is_diverging
            nevals += self.hmc.stats.current["n_leapfrog"]
            if verbose and (self.nadapt_counter + 1) % log_interval == 0:
                lap = timer() - start
                per_eval = lap / nevals
                eta = lap * (self.nadapt / (self.nadapt_counter + 1) - 1)
                print(
                    "Warmup step {}/{} ({:.3g}s/eval  ETA: {:.3g}s)".format(
                        self.nadapt_counter + 1, self.nadapt, per_eval, eta
                    )
                )
                self.hmc.stats.log_current()

        self.hmc.after_sample()

        if not update_states:
            self.hmc.set_optimizer_states(opt_states)

        lap = timer() - start
        per_eval = lap / nevals
        print(
            "Finished warmup after {:.3g}s ({:.3g}s/eval)".format(
                lap, per_eval
            )
        )
        print(
            "{} divergent transitions were encountered during warm-up ({:.3f}%)".format(
                ndivergent, 100 * ndivergent / self.nadapt
            )
        )
        print("Mean statistics:")
        self.hmc.stats.log_mean()
