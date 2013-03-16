import unittest

from yt.finance import lib
from yt.finance.lib import precision


class TestLibrary(unittest.TestCase):

    def test_precision(self):
        """ Test the precision decorator """

        @precision
        def return_numbers():
            return [1.0808, 2.03, {'a': 1.5}]

        self.assertEqual(return_numbers(precision=2), [1.08, 2.03, {'a': 1.5}])

if __name__ == '__main__':
    unittest.main()
