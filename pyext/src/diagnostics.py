import numpy as np
import arviz as az


def get_inference_data(*hmcs, **kwargs):
    """Build an Arviz `InferenceData` instance from 1 or more chains."""
    varnames = kwargs.get("varnames", None)
    if varnames is None:
        varnames = hmcs[0].opt_vars.get_names()

    datasets = []
    for hmc in hmcs:
        posterior = dict(
            zip(varnames, map(np.array, zip(*hmc.sample_saver.get_values())))
        )
        dataset = az.from_dict(
            posterior=posterior, sample_stats=hmc.stats.get_samples()
        )
        datasets.append(dataset)

    dataset = az.concat(*datasets, dim="chain")

    return dataset


def summarize(hmc):
    return az.summary(hmc)


# def check_divergences(stats):
#     div_stats = stats.get_samples("diverging")
#     n = np.sum(div_stats)
#     N = len(div_stats)
#     print('{} of {} iterations ended with a divergence ({:.3f}%)'.format(n, N,
#             100 * n / N))
#     if n > 0:
#         print('  Try running with larger `adapt_delta` to remove the divergences')


# def check_treedepth(stats, max_depth = 10):
#     depth_stats = stats.get_samples("treedepth")
#     n = np.sum(depth_stats == max_depth)
#     N = len(depth_stats)
#     print(('{} of {} iterations saturated the maximum tree depth of {}'
#             + ' ({:.3f}%)').format(n, N, max_depth, 100 * n / N))
#     if n > 0:
#         print('  Run again with `max_depth` set to a larger value to avoid saturation')


# def check_energy(stats):
#     energy_stats = stats.get_samples("energy")
#     ebfmi = az.arviz.bfmi(energy_stats)
#     if ebfmi < 0.2:
#         print('E-BFMI = {}'.format(ebfmi))
#         print('  E-BFMI below 0.2 indicates you may need to reparameterize your model')
#     else:
#         print('E-BFMI indicated no pathological behavior')

# def check_n_eff(stats):
#     """Checks the effective sample size per iteration"""
#     fit_summary = fit.summary(probs=[0.5])
#     n_effs = [x[4] for x in fit_summary['summary']]
#     names = fit_summary['summary_rownames']
#     n_iter = len(fit.extract()['lp__'])

#     no_warning = True
#     for n_eff, name in zip(n_effs, names):
#         ratio = n_eff / n_iter
#         if (ratio < 0.001):
#             print('n_eff / iter for parameter {} is {}!'.format(name, ratio))
#             print('E-BFMI below 0.2 indicates you may need to reparameterize your model')
#             no_warning = False
#     if no_warning:
#         print('n_eff / iter looks reasonable for all parameters')
#     else:
#         print('  n_eff / iter below 0.001 indicates that the effective sample size has likely been overestimated')


# def check_rhat(fit):
#     """Checks the potential scale reduction factors"""
#     from math import isnan
#     from math import isinf

#     fit_summary = fit.summary(probs=[0.5])
#     rhats = [x[5] for x in fit_summary['summary']]
#     names = fit_summary['summary_rownames']

#     no_warning = True
#     for rhat, name in zip(rhats, names):
#         if (rhat > 1.1 or isnan(rhat) or isinf(rhat)):
#             print('Rhat for parameter {} is {}!'.format(name, rhat))
#             no_warning = False
#     if no_warning:
#         print('Rhat looks reasonable for all parameters')
#     else:
#         print('  Rhat above 1.1 indicates that the chains very likely have not mixed')


# def check_all_diagnostics(fit):
#     """Checks all MCMC diagnostics"""
#     check_n_eff(fit)
#     check_rhat(fit)
#     check_div(fit)
#     check_treedepth(fit)
#     check_energy(fit)
