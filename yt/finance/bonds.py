"""
Bonds.py calculates various operations on a bond.
"""


from yt.finance.lib import precision
from yt.finance import lib


class Bond(object):

    face_value = 0  # the face value of the bond
    periods = 0  # the number of periods to calculate
    up_probability = 0  # the probability of the value of the bond increasing
    base_short_rate = 0  # the base short rate to calculate the lattice with
    variance_up = 0  # the variance in the value of a bond as it goes up
    variance_down = 0  # the variance in the value of a bond as it goes down

    def __init__(self, face_value, periods, up_probability, base_short_rate,
                 variance_up, variance_down):
        self.face_value = face_value
        self.periods = periods
        self.up_probability = up_probability
        self.base_short_rate = base_short_rate
        self.variance_up = variance_up
        self.variance_down = variance_down
        self.return_lattice = self.__generate_return_lattice()

    def __generate_return_lattice(self):
        """
        Generates the return lattice
        """
        return_lattice = lib.generate_lattice(self.periods,
                                              self.base_short_rate,
                                              self.variance_up,
                                              self.variance_down)

    @precision
    def price_lattice(self):
        """
        Returns the price lattice of a bond, based off of a lattice model.
        """
        z_final = [[self.face_value for i in range(self.periods + 1)]]
        for i in range(self.periods):
            lattice_column = self.periods - i - 1
            z_column = []
            for j in range(lattice_column + 1):
                value = self.__calculate_bond_value(self.return_lattice[lattice_column][j],
                                                    self.up_probability,
                                                    z_final[0][j], z_final[0][j + 1])
                z_column.append(value)
            z_final.insert(0, z_column)
        z_column.append(value)
        return z_final

    @precision
    def price_american_put(self, periods, strike_price):

        def american_price(lattice=None, return_lattice=None, col=0, row=0):
            sell_now_price = lattice[col][row] - strike_price
            asset_value = self.__calculate_bond_value(self.return_lattice[col][row],
                                                      self.up_probability,
                                                      return_lattice[0][row],
                                                      return_lattice[0][row + 1])
            return max(0, sell_now_price, asset_value)

        return lib.price_lattice(periods,
                                 self.price_lattice(),
                                 [max(0, self.face_value - self.strike_price) for i in range(periods + 1)],
                                 american_price)[0][0]

    @precision
    def price(self):
        return self.price_lattice()[0][0]

    def __calculate_bond_value(self, short_rate, up_probability, up_value, down_value):
        return (1 / (1 + short_rate)) * (up_probability * up_value + (1 - up_probability) * down_value)
