"""
encapsulates a portfolio
"""

from numpy import array, matrix, multiply
import numpy as np

from lib import precision


class Portfolio(object):
    """ Represents a single portfolio """
    assets = None  # numpy array, list of assets and their returns
    asset_count = None  # number of assets
    covariance = None  # numpy matrix, covariance matrix
    distributions = None  # numpy array, distribution of assets
    risk_free_return = None  # the risk-free return, if it exists

    def __init__(self, assets, distributions, covariance, risk_free_return=None):
        self.assets = array(assets)
        self.asset_count = len(self.assets)
        self.distributions = array(distributions)
        self.covariance = matrix(covariance)
        self.risk_free_return = risk_free_return

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
        1.33
        """
        distributions_matrix = matrix(self.distributions)
        distributions_matrix = distributions_matrix * self.covariance * distributions_matrix.transpose()
        return np.sqrt(distributions_matrix.sum())

    @precision
    def minimize_variance(self, desired_return):
        """
        Optimized the distribution of the assets provided. (this ignores distributions)

        >>> p.minimize_variance(0.05, precision=2)
        [0.0, 1.0, 0.0]
        """
        # generate the system of lagrange equations to solve
        lagrange_equations = np.zeros((self.asset_count + 2, self.asset_count + 2))
        lagrange_equations[:self.asset_count, :self.asset_count] = np.multiply(self.covariance, 2)
        lagrange_equations[self.asset_count, :self.asset_count] = self.assets
        lagrange_equations[self.asset_count + 1, :self.asset_count] = np.ones((1, self.asset_count))
        lagrange_equations[:self.asset_count, self.asset_count] = \
            np.multiply(self.assets.transpose(), -1)
        lagrange_equations[:self.asset_count, self.asset_count + 1] = \
            np.multiply(np.ones((1, self.asset_count)), -1)
        solutions = np.zeros((self.asset_count + 2, 1))
        solutions[self.asset_count + 1] = 1
        solutions[self.asset_count] = desired_return
        return [x.item(0) for x in (matrix(lagrange_equations).I * solutions)[:self.asset_count]]

    @precision
    def optimal_sharp_ratio(self):
        """
        Calculate the optimal sharp ratio

        >>> p.optimal_sharp_ratio()
        0
        """
        assert self.risk_free_return, \
            "No risk free return found! Cannot calculate sharp ration without risk free return!"
        excess_returns = self.assets - multiply(np.ones(self.asset_count), self.risk_free_return)
        positions = excess_returns * self.covariance.I
        position_sum = positions.sum()
        sharp_optimal_portfolio = multiply(positions, 1.0 / position_sum)
        mean_excess_return = sharp_optimal_portfolio.dot(excess_returns).sum()
        # refactor this out
        distributions_matrix = matrix(sharp_optimal_portfolio)
        distributions_matrix = distributions_matrix * self.covariance * distributions_matrix.transpose()
        volatility = np.sqrt(distributions_matrix.sum())
        import pdb; pdb.set_trace()
        return mean_excess_return / volatility
