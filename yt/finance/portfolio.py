"""
encapsulates a portfolio
"""
from numpy import array, matrix, multiply

from lib import precision


class Portfolio(object):
    """ Represents a single portfolio """
    assets = None  # numpy array, list of assets and their returns
    covariance = None  # numpy matrix, covariance matrix
    distributions = None  # numpy array, distribution of assets

    def __init__(self, assets, distributions, covariance):
        self.assets = array(assets)
        self.distributions = array(distributions)
        self.covariance = matrix(covariance)

    @precision
    def mean_return(self):
        """
        Return the mean return of the portfolio

        >>> p.mean_return(precision=2)
        0.05
        """
        return self.assets.dot(self.distributions)

    @precision
    def volatility(self):
        """
        Return the volatility of the portfolio

        sum((distributions * distributions^ ) .* covariance)
        >>> p.volatility(precision=2)
        1.78
        """
        distributions_matrix = matrix(self.distributions)
        distributions_matrix = distributions_matrix.transpose() * distributions_matrix
        return multiply(self.covariance, distributions_matrix).sum()
