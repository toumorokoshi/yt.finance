import doctest
import yt.finance.binomial
import yt.finance.interest
from yt.finance.binomial import Binomial


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(module=yt.finance.binomial,
                                        extraglobs={'b': Binomial()}))
    tests.addTests(doctest.DocTestSuite(module=yt.finance.interest))
    return tests
