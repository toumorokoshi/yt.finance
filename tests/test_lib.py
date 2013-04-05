import unittest

from yt.finance import lib
from yt.finance.lib import precision, generate_lattice


class TestLibrary(unittest.TestCase):

    def test_precision(self):
        """ Test the precision decorator """

        @precision
        def return_numbers():
            return [1.0808, 2.03, {'a': 1.5}]

        self.assertEqual(return_numbers(precision=2), [1.08, 2.03, {'a': 1.5}])

    def test_lattice(self):
        lattice = generate_lattice(5, 0.06, 1.25, 0.9, precision=2)
        self.assertEqual(lattice, [[0.06],
                                   [0.07, 0.05],
                                   [0.09, 0.07, 0.05],
                                   [0.12, 0.08, 0.06, 0.04],
                                   [0.15, 0.11, 0.08, 0.05, 0.04],
                                   [0.18, 0.13, 0.09, 0.07, 0.05, 0.04]], "Lattice was not as expected!")

if __name__ == '__main__':
    unittest.main()
