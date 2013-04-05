import unittest

from yt.finance.bonds import Bond


class TestBonds(unittest.TestCase):

    def setUp(self):
        self.bond = Bond(100, 4, 0.5, 0.06, 1.25, 0.9)

    def test_bond_price(self):
        """
        Test the bond price
        """
        self.assertEqual(self.bond.price(precision=2), 77.22)
