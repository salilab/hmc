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
