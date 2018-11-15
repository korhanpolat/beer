'''Implementation of the Normaldistribution.'''

import math
import torch
from .baseprior import ExpFamilyPrior
from .wishart import _logdet


class NormalFullCovariancePrior(ExpFamilyPrior):
    '''Normal distribution with full covariance matrix.

    parameters:
        mean: mean of the distribution
        cov: covariatnce matrix

    natural parameters:
        eta1 = cov^{-1} * mean
        eta2 = - 0.5 * cov^{-1}

    sufficient statistics:
        T_1(x) = x
        T_2(x) = x * x^T

    '''

    def __init__(self, mean, cov):
        self._dim = len(mean)
        nparams = self.to_natural_parameters(mean, cov)
        super().__init__(nparams)

    def __repr__(self):
        return f'{self.__class__.__qualname__}(mean={self.mean}, cov={self.cov})'

    @property
    def dim(self):
        return self._dim

    @property
    def mean(self):
        return self.to_std_parameters(self.natural_parameters)[0]

    @property
    def cov(self):
        return self.to_std_parameters(self.natural_parameters)[1]

    def moments(self):
        stats = self.expected_sufficient_statistics()
        return stats[:self.dim], stats[self.dim:]

    def expected_value(self):
        mean, _ = self.to_std_parameters(self.natural_parameters)
        return mean

    def to_natural_parameters(self, mean, cov):
        prec = cov.inverse()
        return torch.cat([prec @ mean, -.5 * prec.reshape(-1)])

    def _to_std_parameters(self, natural_parameters=None):
        if natural_parameters is None:
            natural_parameters = self.natural_parameters
        precision = - 2 * natural_parameters[self.dim:]
        cov = precision.reshape(self.dim, self.dim).inverse()
        mean = cov @ natural_parameters[:self.dim:]
        return mean, cov

    def _expected_sufficient_statistics(self):
        mean, cov = self.to_std_parameters(self.natural_parameters)
        return torch.cat([
            mean,
            (cov + torch.ger(mean, mean)).reshape(-1)
        ])

    def _log_norm(self, natural_parameters=None):
        if natural_parameters is None:
            natural_parameters = self.natural_parameters
        mean, cov = self.to_std_parameters(natural_parameters)
        precision = -2 * natural_parameters[self.dim:]
        precision = precision.reshape(self.dim, self.dim)
        log_norm = .5 * mean @ precision @ mean
        log_norm -= .5 * _logdet(precision).sum()
        return log_norm + .5 * self.dim * math.log(2*math.pi)


__all__ = ['NormalFullCovariancePrior']

