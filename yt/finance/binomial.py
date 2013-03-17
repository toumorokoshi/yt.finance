"""
Price.py

A set of pricing tools for various options
"""
__author__ = 'yusuke tsutsumi'

import math

from yt.finance.lib import precision

PERIODS = 1


class Binomial(object):
    """
    Price with the binomial model
    """
    times = 1
    strike_price = None  # initial price of a stock
    periods = 1  # number of periods in the pricing range
    return_price = None  # return on investment

    def __init__(self, **kwargs):
        if 'times' in kwargs:
            self.times = kwargs['times']
        if 'return_price' in kwargs:
            self.return_price = kwargs['return_price']

    def convert_black_sholes_params(self, periods, maturity, interest_rate,
                                    strike_price, volatility, dividend_yield):
        """
        Returns parameters to the binomial model from parameters for
        the black sholes model

        returns the market_return, gain, and the dividend

        >>> b.convert_black_sholes_params(15, 0.25, 0.02, 110, 0.3, 0.01)
        (1.0003333888950623, 1.0394896104013376, 0.00016670833873502509)
        """
        market_return = math.e ** (1.0 * interest_rate * maturity / periods)
        gain = math.e ** (volatility * math.sqrt(1.0 * maturity / periods))
        dividend = market_return * (1.0 - (math.e ** - (1.0 * dividend_yield * maturity / periods)))
        return (market_return, gain, dividend)

    @precision
    def price_american_put(self, periods, strike_price, market_return, security_volatility, stock_lattice, dividend=0):
        """
        Get price of an american put.

        >>> lattice = b.generate_stock_lattice(3, 110, 1.07)
        >>> b.price_american_put(3, 100, 1.01, 1.07, lattice, precision=2)
        [[0, 0, 0, 10.21], [0.0, 0.0, 4.48], [0.0, 1.96], [0.86]]
        """
        # first initialize a matrix to house the results
        return_values = []
        # value for the last column starts at (price_matrix_value - strike_price)
        return_values.append(
            [(strike_price - x if strike_price - x > 0 else 0) \
                for x in stock_lattice[periods]])
        for i in range(periods):
            return_column = []
            for j in range(periods - i):
                price = self._calculate_security_pricing(
                            market_return,
                            security_volatility,
                            return_values[i][j],
                            return_values[i][j + 1],
                            dividend=dividend)
                excersize_now_price = strike_price - stock_lattice[periods - 1 - i][j]
                if price < excersize_now_price:
                    price = excersize_now_price
                return_column.append(price)
            return_values.append(return_column)
        return return_values
        pass

    @precision
    def price_european_call(self, periods, strike_price, market_return, security_volatility, stock_lattice, dividend=0):
        """
        Get price of a european call.

        This utilizes the binomial model to calculate the expirations
        of various prices, and uses dynamic programming to solve the
        call prices and periods from periods to period zero.

        if precision is greater than 0, the result is rounded to precision decimals.

        >>> lattice = b.generate_stock_lattice(3, 100, 1.07)
        >>> b.price_european_call(3, 100, 1.01, 1.07, lattice, precision=2)
        [[22.5, 7.0, 0, 0], [15.48, 3.86, 0.0], [10.23, 2.13], [6.57]]
        """
        # starting at the end, work backwards to find the proper values of the matrix.
        return_values = []
        # value for the last column starts at (price_matrix_value - strike_price)
        return_values.append(
            [(x - strike_price if x - strike_price > 0 else 0) \
                for x in stock_lattice[periods]])
        for i in range(periods):
            return_column = []
            for j in range(periods - i):
                price = self._calculate_security_pricing(
                            market_return,
                            security_volatility,
                            return_values[i][j],
                            return_values[i][j + 1],
                            dividend=dividend)
                return_column.append(price)
            return_values.append(return_column)
        return return_values

    @precision
    def generate_stock_lattice(self, periods, initial_price, security_volatility):
        """
        Generate a price matrix of the security in various conditions,
        at each possible outcome.

        Outcome is rounded to accurracy digits

        >>> b.generate_stock_lattice(3, 100, 1.07, precision=2)
        [[100.0], [107.0, 93.46], [114.49, 100.0, 87.34], [122.5, 107.0, 93.46, 81.63]]
        """
        return_values = []
        for i in range(periods + 1):
            return_column = []
            for j in range(i):
                price = self._calculate_price(initial_price, security_volatility, i - j, j)
                return_column.append(price)
            price = self._calculate_price(initial_price, security_volatility, 0, i)
            return_column.append(price)
            return_values.append(return_column)
        return return_values

    @precision
    def _calculate_price(self, initial_price, security_volatility, positive_changes, negative_changes):
        """
        Calculate and return the price of an underlying security after
        positive_changes price increases and negative_changes price
        decreases.

        >>> round(b._calculate_price(100, 1.10, 5, 3), 2)
        121.0
        """
        return initial_price * (security_volatility ** positive_changes) * \
            ((1.0 / security_volatility) ** negative_changes)

    @precision
    def _calculate_security_pricing(self, market_return, security_volatility, gain_price, loss_price, dividend=0):
        """
        This calculates the price of a security at the start of time, with risk-neutral pricing.

        We start with these values:
        * The standard return of the market R = market_return
        * The possible gain proportion u = security_volatility
        * The possible loss proportion d = 1 / security_volatility
        * The value of the security in the case of a gain Cu = gain_price
        * The value of the security in the case of a loss Cd = loss_price

        And try to find the security price C0

        By the arbitrage principle, we must ensure that the price of
        the security reflects the profit it provides over other means
        of investments. Thus, we find the total amount that needs to
        be invested in the security and other investments:

        u*s0*x + R*y = Cu
        d*s0*x + R*y = Cd
        C0 = x*s0 + y

        solving, we end up with:

        C0 = (1/R)*((R-d)/(u-d)*Cu + (u-R)/(u-d)*Cd)

        >>> round(b._calculate_security_pricing(1.01, 1.07, 5, 0), 2)
        2.76
        """
        security_probability = self._risk_neutral_probability(market_return,
                                                              security_volatility,
                                                              dividend=dividend)
        return (1 / market_return) * ((security_probability * gain_price) +
                                          ((1 - security_probability) * loss_price))

    @precision
    def _risk_neutral_probability(self, market_return, security_volatility, dividend=0):
        """
        Return the probabilities that emerge from a perfectly
        competitive market.

        I.E. given the provided market return,
        possible gain ratio, and possible loss ratio of a security, the returned value
        is the probability of a gain required to ensure that the security
        provides the same risk as any other investment in the market.

        >>> round(b._risk_neutral_probability(1.01, 1.07), 3)
        0.557

        >>> round(b._risk_neutral_probability(1.0003333888950623, 1.0394896104013376, 0.00016670833873502509), 4)
        0.4925

        TODO ONE MORE TEST FOR DIVIDEND_YIELD
        """
        return (1.0 * market_return - (1 / security_volatility) - dividend) \
            / (security_volatility - (1 / security_volatility))


if __name__ == '__main__':
    import doctest
    doctest.testmod(extraglobs={
            'b': Binomial()
    }, verbose=True)
