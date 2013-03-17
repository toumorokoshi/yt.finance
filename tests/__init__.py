import doctest
import yt.finance.binomial
from yt.finance.binomial import Binomial


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(module=yt.finance.binomial,
                                        extraglobs={'b': Binomial()}))
    return tests
