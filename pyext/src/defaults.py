from .variables import OptimizedVariables
from .log_density import LogDensity, TransformedLogDensity
from .hmc import HamiltonianMonteCarlo
from .adaptor import Adaptor


def setup_warmup_hmc(
    sf,
    hmc_type="dynamic",
    max_depth=10,
    metric="diag",
    save_warmup=False,
    warmup_optimizer_states=[],
    nadapt=1000,
    adapt_delta=0.8,
    log_freq=0.1,
    verbose=False,
    shuffle=False,
    shuffle_sigma=1,
):
    m = sf.get_model()
    hmc_vars = OptimizedVariables(m)
    if shuffle:
        hmc_vars.shuffle(shuffle_sigma)
    interface = hmc_vars.get_interface()
    transformation = hmc_vars.get_transformation()
    logpdf = TransformedLogDensity(LogDensity(sf, interface), transformation)
    hmc = HamiltonianMonteCarlo(
        sf,
        hmc_vars,
        logpdf,
        hmc_type=hmc_type,
        max_depth=max_depth,
        metric=metric,
        save_samples=save_warmup,
    )
    hmc.add_optimizer_states(warmup_optimizer_states)

    if nadapt > 0:
        adaptor = Adaptor(hmc, nadapt=nadapt, adapt_delta=adapt_delta)
        adaptor.adapt(log_freq=log_freq, verbose=verbose)
        adapt_stats = hmc.stats
        adapt_samples = hmc.sample_saver.get_values()
        hmc.stats = None
        hmc.samples = None
        return hmc, adapt_stats, adapt_samples

    return hmc


def setup_warmup_run_hmc(
    sf,
    nsample=2000,
    save_samples=True,
    sample_optimizer_states=[],
    **warmup_kwargs
):
    hmc = setup_warmup_hmc(sf, **warmup_kwargs)
    if "nadapt" not in warmup_kwargs or warmup_kwargs["nadapt"] > 0:
        hmc, _, _ = hmc

    print("Sampling from HMC for {0} steps.".format(nsample))
    hmc.set_save_samples(save_samples)
    hmc.add_optimizer_states(sample_optimizer_states)
    hmc.optimize(nsample)

    hmc.stats.log_mean()

    return hmc
