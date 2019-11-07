import IMP
import numpy as np

from .hamiltonian import Hamiltonian
from .accumulator import SampleAccumulator, StatisticsAccumulator
from .julia import Main, HMCUtilities, AdvancedHMC


class HamiltonianMonteCarlo(IMP.Optimizer):

    _stats_key_map = {
        "log_density": "lp",
        "acceptance_rate": "accept_stat",
        "step_size": "stepsize",
        "tree_depth": "treedepth",
        "n_steps": "n_leapfrog",
        "numerical_error": "diverging",
        "hamiltonian_energy": "energy",
    }

    def __init__(
        self,
        sf,
        opt_vars,
        logpdf,
        hmc_type="dynamic",
        max_depth=10,
        metric="diag",
        save_samples=False,
        name="HamiltonianMonteCarlo%1%",
    ):
        m = sf.get_model()
        super().__init__(m, name)
        self.set_scoring_function(sf)
        self.opt_vars = opt_vars
        self.interface = opt_vars.get_interface()
        self.transformation = opt_vars.get_transformation()
        self.hamiltonian = Hamiltonian(logpdf, metric=metric)
        self.phasepoint = None
        self.integrator = None
        self.sampler = None
        self.create_integrator()
        self.create_sampler(hmc_type=hmc_type, max_depth=max_depth)
        self.max_depth = max_depth
        self.create_phasepoint()
        self.stats = None
        self.sample_saver = IMP.hmc.SaveAttributesOptimizerState(self.interface)
        self.set_save_samples(save_samples)

    def get_save_samples(self):
        return self._save_samples

    def set_save_samples(self, tf):
        self.remove_optimizer_state(self.sample_saver)
        if tf:
            self._save_samples = True
            self.add_optimizer_state(self.sample_saver)
        else:
            self._save_samples = False

    def init_step_size(self):
        print("Initializing step size")
        return AdvancedHMC.find_good_eps(
            self.hamiltonian.hamiltonian,
            HMCUtilities.free(
                self.transformation, self.interface.get_values()
            ),
        )

    def create_integrator(self):
        eps = self.init_step_size()
        self.integrator = AdvancedHMC.Leapfrog(eps)

    def create_sampler(self, hmc_type="dynamic", max_depth=10):
        if hmc_type == "dynamic":
            self.sampler = Main.eval(
                "AdvancedHMC.NUTS{AdvancedHMC.MultinomialTS,AdvancedHMC.GeneralisedNoUTurn}"
            )(self.integrator, max_depth)
        elif hmc_type == "static":
            self.sampler = AdvancedHMC.StaticTrajectory(self.integrator)
        else:
            raise ValueError("'hmc_type' must be in {'dynamic', 'static'}")

    def create_phasepoint(self):
        self.phasepoint = HMCUtilities.make_phasepoint(
            self.hamiltonian.hamiltonian,
            HMCUtilities.free(
                self.transformation, self.interface.get_values()
            ),
        )

    def do_get_inputs(self):
        return [
            self.get_model().get_particle(pi)
            for pi in self.interface.get_particle_indexes()
        ]

    def do_optimize(self, ns):
        self.before_optimize()
        for n in range(ns):
            self.before_sample()
            self.sample()
            self.after_sample()
        self.after_optimize()
        return self.get_scoring_function().get_last_score()

    def before_optimize(self):
        self.get_scoring_function().evaluate(True)
        self.create_phasepoint()

    def after_optimize(self):
        self.get_model().update()

    def is_adapting(self):
        return self.adaptor is not None or self.adaptor.is_adapting()

    @property
    def is_diverging(self):
        return self.stats.current["diverging"]

    @property
    def step_size(self):
        return HMCUtilities.step_size(self.integrator)

    def sample(self):
        self.phasepoint, stats = HMCUtilities.sample(
            self.hamiltonian.hamiltonian, self.sampler, self.phasepoint
        )

        stats = Main.pairs(stats)
        stats.pop("is_accept")
        try:
            self.stats.add_sample(stats)
        except AttributeError:
            stats_keys = [self._stats_key_map[k] for k in stats.keys()]
            self.stats = StatisticsAccumulator(stats_keys)
            self.stats.add_sample(stats)

    def before_sample(self):
        pass

    def after_sample(self):
        self.interface.set_values(
            HMCUtilities.constrain(
                self.transformation,
                HMCUtilities.position(self.phasepoint)
            )
        )
        if self.get_has_optimizer_states():
            self.get_model().update()
            self.update_states()
