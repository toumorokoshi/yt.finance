import doctest
import yt.finance.binomial
import yt.finance.interest
import yt.finance.portfolio
from yt.finance.binomial import Binomial
from yt.finance.portfolio import Portfolio

assets = [0.06, 0.05, 0.04]
distributions = [1.0 / 3, 1.0 / 3, 1.0 / 3]
covariance = [
    [6.0, -2.0, 4.0],
    [-2.0, -2.0, 2.0],
    [4.0, -2.0, 8.0]
]
risk_free_return = 0.01


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(module=yt.finance.binomial,
                                        extraglobs={'b': Binomial()}))
    tests.addTests(doctest.DocTestSuite(module=yt.finance.interest))
    tests.addTests(doctest.DocTestSuite(module=yt.finance.portfolio,
                                        extraglobs={'p': Portfolio(assets, distributions, covariance, risk_free_return)}))
    return tests
