import numpy as np

from .julia import AdvancedHMC


def is_approx_identity_matrix(M):
    M = np.asarray(M)
    return np.all(np.isclose(M, np.eye(*M.shape)))


def is_approx_diagonal_matrix(M):
    M = np.asarray(M)
    return np.all(np.isclose(M, np.diag(np.diag(M))))


def is_positive_definite_matrix(x):
    return np.all(np.linalg.eigvals(x) > 0)


class Hamiltonian(object):

    """Currently just a thin wrapper for an `AdvancdHMC.Hamiltonian`."""

    def __init__(self, log_density, metric="diag"):
        self.logpdf = log_density
        self.create_hamiltonian(metric)

    def create_metric(self, metric):
        try:
            M = np.array(metric, dtype=np.double)
            m, n = np.shape
            if m != n or n != self.logpdf.get_dimension():
                raise ValueError(
                    "Metric matrix must be square with the same size in each ",
                    "dimension as the number of free variables",
                )
            if is_approx_identity_matrix(M):
                return AdvancedHMC.UnitEuclideanMetric(n)
            elif is_approx_diagonal_matrix(M):
                return AdvancedHMC.DiagEuclideanMetric(M)
            elif is_positive_definite_matrix(M):
                return AdvancedHMC.DenseEuclideanMetric(M)
            else:
                raise ValueError("Metric matrix is not positive definite")
        except ValueError:
            pass

        n = self.logpdf.get_dimension()
        if metric == "unit":
            return AdvancedHMC.UnitEuclideanMetric(n)
        elif metric == "diag":
            return AdvancedHMC.DiagEuclideanMetric(n)
        elif metric == "dense":
            return AdvancedHMC.DenseEuclideanMetric(n)
        else:
            raise ValueError(
                "metric_type must be either a matrix or ",
                "{'unit', 'diag', 'dense'}",
            )

    @property
    def metric(self):
        return self.hamiltonian.metric

    def create_hamiltonian(self, metric):
        metric = self.create_metric(metric)
        self.hamiltonian = AdvancedHMC.Hamiltonian(
            metric,
            self.logpdf.get_logpdf,
            self.logpdf.get_logpdf_with_gradient,
        )

    def get_energy(self):
        return AdvancedHMC.energy(self.hamiltonian)
