"""
This module provides methods to deal with pricing commodities which
deal with a constant, compounding interest.
"""
from yt.finance.lib import precision


@precision
def swap(periods, rates):
    """
    Calculate the fair swap interest rate, over n periods, with the
    rates for the periods in a list rates.

    >>> swap(6, [0.07, 0.073, 0.077, 0.081, 0.084, 0.088], precision=3)
    0.086
    """
    assert len(rates) >= periods, "rates must be provided for each period!"
    return (1 - rate(0, periods, rates)) / sum([rate(0, i + 1, rates) for i in range(periods)])


@precision
def forward_price(price, annual_interest, compound_rate, time):
    """
    Generates the forward price of a stock that:
    * starts at price
    * has an annual interest annual_interest
    * compounds at compound_rate (n times a year)
    * delivery at time, in years

    >>> forward_price(400, 0.08, 4, 0.75, precision=2)
    424.48
    """
    return price / rate(0, int(time * compound_rate),
        [annual_interest / compound_rate for x in range(int(time * compound_rate))])


@precision
def present_value(periods, income_list, interest):
    """
    Provides present value of a commodity

    periods = # of periods
    income_list = list of income for each period
    interest = percentage interest rate applied per period

    >>> present_value(20, [0.5 for i in range(20)], 0.1, precision=2)
    4.68
    """
    assert len(income_list) >= periods, "The income_list must specify incomes for every period!"
    return sum([income_list[i] / ((1 + interest) ** i) for i in range(periods)])


@precision
def rate(start, stop, rates):
    """
    calculates either a discount rate or a forward rate between start and stop, with an list of
    discount_rates with indices at least until at least the stop date.

    >>> rate(0, 2, [0.063, 0.069], precision=3)
    0.875

    >>> rate(1, 2, [0.063, 0.069], precision=3)
    0.075
    """
    assert len(rates) >= stop, "discount rates must have discount rates " + \
        "for every year until the stop date!"
    # checking if it's a discount rate, or a forward rate
    if start == 0:
        return 1 / ((1 + rates[stop - 1]) ** stop)
    else:
        power = (1 / (stop - start))
        return (((1 + rates[stop - 1]) ** stop) /
                ((1 + rates[start - 1]) ** start)) ** power - 1

if __name__ == '__main__':
    import doctest
    doctest.testmod()
