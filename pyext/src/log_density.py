import numpy as np

from .julia import Main, HMCUtilities


class LogDensityBase(object):
    def get_dimension(self):
        raise NotImplementedError

    def get_logpdf(self, x):
        raise NotImplementedError

    def get_logpdf_with_gradient(self, x):
        raise NotImplementedError


class LogDensity(LogDensityBase):
    def __init__(self, sf, interface):
        super().__init__()

        self.sf = sf
        self.interface = interface

    def get_dimension(self):
        return self.interface.get_dimension()

    def get_logpdf(self, x):
        self.interface.set_values(x)
        return -self.sf.evaluate(False)

    def get_logpdf_with_gradient(self, x):
        self.interface.set_values(x)
        V = self.sf.evaluate(True)
        grad = np.asarray(self.interface.get_gradient(), dtype=np.double)
        return -V, -grad


class TransformedLogDensity(LogDensityBase):
    def __init__(self, logpdf, transform):
        super().__init__()

        self.logpdf = logpdf
        self.transform = transform

        # Use hash for unique name
        jcname = "Main.jc{}".format(self.__hash__())
        exec("{0} = self.transform".format(jcname))
        self.constrain_with_pushlogpdf = Main.eval(
            "PyCall.pyfunction(y->HMCUtilities.constrain_with_pushlogpdf({0}, y), Vector{{Float64}})".format(
                jcname
            )
        )

    def get_dimension(self):
        return HMCUtilities.free_dimension(self.transform)

    def get_logpdf(self, y):
        x, pushlogpdf = self.constrain_with_pushlogpdf(y)
        logpdf_x = self.logpdf.get_logpdf(x)
        return pushlogpdf(logpdf_x)

    def get_logpdf_with_gradient(self, y):
        x, pushlogpdf = self.constrain_with_pushlogpdf(y)
        logpdf_x, gradx_logpdf_x = self.logpdf.get_logpdf_with_gradient(x)
        return pushlogpdf(logpdf_x, gradx_logpdf_x)
