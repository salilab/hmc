import datetime
from timeit import default_timer as timer

from .julia import HMCUtilities, AdvancedHMC


class Adaptor(object):

    """Adapt the step size and metric during warm-up.

    Currently just a thin wrapper for an `AdvancedHMC.StanHMCAdaptor`."""

    def __init__(self, hmc, nadapt=2000, adapt_delta=0.8):
        self.hmc = hmc
        self.create_adaptor(nadapt, adapt_delta=adapt_delta)
        self.nadapt = nadapt

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
            HMCUtilities.position(self.hmc.phasepoint),
            self.hmc.stats.current["mean_tree_accept"],
        )
        self.hmc.hamiltonian.hamiltonian = AdvancedHMC.reconstruct(
            self.hmc.hamiltonian.hamiltonian, self.adaptor
        )
        self.hmc.sampler = AdvancedHMC.reconstruct(self.hmc.sampler, self.adaptor)
        self.nadapt_counter += 1

    def adapt(
        self, update_states=False, log_freq=0.01, log_prec=3, verbose=True
    ):
        print("Warming up HMC for {0} steps.".format(self.nadapt))

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
            nevals += self.hmc.stats.current["tree_size"]
            if verbose and (self.nadapt_counter + 1) % log_interval == 0:
                lap = timer() - start
                per_eval = lap / nevals
                eta = lap * (self.nadapt / (self.nadapt_counter + 1) - 1)
                print(
                    "Warmup step {0}/{1} ({2:.{4}g}s/eval  ETA: {3})".format(
                        self.nadapt_counter + 1,
                        self.nadapt,
                        per_eval,
                        datetime.timedelta(seconds=eta),
                        log_prec,
                    )
                )
                self.hmc.stats.log_mean()

        self.hmc.after_sample()

        if not update_states:
            self.hmc.set_optimizer_states(opt_states)

        lap = timer() - start
        per_eval = lap / nevals
        print(
            "Finished warmup after {0:.{2}g}s ({1:.{2}g}s/eval)".format(
                lap, per_eval, log_prec
            )
        )
        print(
            "{0} divergent transitions were encountered during warm-up ({1:.{2}%}%)".format(
                ndivergent, ndivergent / self.nadapt, log_prec
            )
        )
        self.hmc.stats.log_mean(title="Mean warm-up statistics:")
