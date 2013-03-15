"""
Price.py

A set of pricing tools for various options
"""
__author__ = 'yusuke tsutsumi'

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

    def price_american_put(self, periods, strike_price, market_return, security_volatility, accuracy=0):
        """
        Get price of an american put.

        >>> b.price_american_put(4, 100, 1.01, 1.07, accuracy=2)
        []
        """
        # first initialize a matrix to house the results
        price_matrix = self._generate_price_matrix(periods, strike_price, security_volatility)
        return_values = []
        # value for the last column starts at (price_matrix_value - strike_price)
        return_values.append(
            [(self._round(strike_price - x, accuracy) if strike_price - x > 0 else 0) \
                for x in price_matrix[periods - 1]])
        for i in range(periods - 1):
            return_column = []
            for j in range(periods - 1 - i):
                price = self._calculate_security_pricing(
                            price_matrix[periods - 2 - i][j],
                            market_return,
                            security_volatility,
                            return_values[i][j],
                            return_values[i][j + 1])
                excersize_now_price = strike_price - price_matrix[periods - 2 - i][j]
                if price < excersize_now_price:
                    price = excersize_now_price
                return_column.append(self._round(price, accuracy))
            return_values.append(return_column)
        return return_values
        pass

    def price_european_call(self, periods, strike_price, market_return, security_volatility, accuracy=0):
        """
        Get price of a european call.

        This utilizes the binomial model to calculate the expirations
        of various prices, and uses dynamic programming to solve the
        call prices and periods from periods to period zero.

        if accuracy is greater than 0, the result is rounded to accuracy decimals.

        >>> b.price_european_call(4, 100, 1.01, 1.07, accuracy=2)
        [[22.5, 7.0, 0, 0], [15.48, 3.86, 0.0], [10.23, 2.13], [6.58]]
        """
        # first initialize a matrix to house the results
        price_matrix = self._generate_price_matrix(periods, strike_price, security_volatility)
        # starting at the end, work backwards to find the proper values of the matrix.
        return_values = []
        # value for the last column starts at (price_matrix_value - strike_price)
        return_values.append(
            [(self._round(x - strike_price, accuracy) if x - strike_price > 0 else 0) \
                for x in price_matrix[periods - 1]])
        for i in range(periods - 1):
            return_column = []
            for j in range(periods - 1 - i):
                price = self._round(self._calculate_security_pricing(
                            price_matrix[periods - 2 - i][j],
                            market_return,
                            security_volatility,
                            return_values[i][j],
                            return_values[i][j + 1]), accuracy)
                return_column.append(price)
            return_values.append(return_column)
        return return_values

    def _round(self, value, accuracy=0):
        """
        A self-implemented round method, to ignore rounding, instead of integer accuracy

        >>> b._round(1.0903709739)
        1.0903709739
        >>> b._round(1.09709709, 2)
        1.1
        """
        return round(value, accuracy) if accuracy > 0 else value

    def _generate_price_matrix(self, periods, strike_price, security_volatility, accuracy=0):
        """
        Generate a price matrix of the security in various conditions,
        at each possible outcome.

        Outcome is rounded to accurracy digits

        >>> b._generate_price_matrix(4, 100, 1.07, accuracy=2)
        [[100.0], [107.0, 93.46], [114.49, 100.0, 87.34], [122.5, 107.0, 93.46, 81.63]]
        """
        return_values = []
        for i in range(periods):
            return_column = []
            for j in range(i):
                price = self._round(
                    self._calculate_price(strike_price, security_volatility, i - j, j),
                    accuracy=accuracy)
                return_column.append(price)
            price = self._round(self._calculate_price(strike_price, security_volatility, 0, i),
                                accuracy=accuracy)
            return_column.append(price)
            return_values.append(return_column)
        return return_values

    def _calculate_price(self, strike_price, security_volatility, positive_changes, negative_changes):
        """
        Calculate and return the price of strike price after
        positive_changes price increases and negative_changes price
        decreases.

        >>> round(b._calculate_price(100, 1.10, 5, 3), 2)
        121.0
        """
        return strike_price * (security_volatility ** positive_changes) * \
            ((1.0 / security_volatility) ** negative_changes)

    # maybe use this
    def _populate_data(self, arg_dict):
        """
        Parse a dictionary and return a tuple of values, either
        populated by the binomial class's default or the value passed.
        """
        strike_price = arg_dict['strike_price'] if 'strike_price' in arg_dict else self.strike_price
        periods = arg_dict['periods'] if 'periods' in arg_dict else self.periods
        market_return = arg_dict['market_return'] if 'market_return' in arg_dict else self.market_return
        security_volatility = arg_dict['security_volatility'] if 'security_volatility' in arg_dict \
            else self.security_volatility
        return (strike_price, periods)

    def _calculate_security_pricing(self, strike_price, market_return, security_volatility, gain_value, loss_value):
        """
        This calculates the price of a security at the start of time, with risk-neutral pricing.

        We start with these values:
        * An initial price for the security S0 = strike_price
        * The standard return of the market R = market_return
        * The possible gain proportion u = security_volatility
        * The possible loss proportion d = 1 / security_volatility
        * The value of the security in the case of a gain Cu = gain_value
        * The value of the security in the case of a loss Cd = loss_value

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

        >>> round(b._calculate_security_pricing(100, 1.01, 1.07, 5, 0), 2)
        2.76
        """
        security_probability = self._risk_neutral_probability(market_return, security_volatility)
        return (1 / market_return) * ((security_probability * gain_value) +
                                          ((1 - security_probability) * loss_value))

    def _risk_neutral_probability(self, market_return, security_volatility):
        """
        Return the probabilities that emerge from a perfectly
        competitive market.

        I.E. given the provided market return,
        possible gain ratio, and possible loss ratio of a security, the returned value
        is the probability of a gain required to ensure that the security
        provides the same risk as any other investment in the market.

        >>> round(b._risk_neutral_probability(1.01, 1.07), 3)
        0.557
        """
        return (1.0 * market_return - (1 / security_volatility)) / (security_volatility - (1 / security_volatility))


if __name__ == '__main__':
    import doctest
    doctest.testmod(extraglobs={
            'b': Binomial()
    })
