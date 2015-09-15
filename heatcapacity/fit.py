#  -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import *

from scipy import interpolate, linalg, signal


class FirstOrder(signal.lti):
    """First order heat capacity differential equation model.

    The first oder heat capacity differential equation is

        C * dy/dt + K * y = u

    with C the heat capacity, K the thermal conductivity, y the temperature and
    u the heater power. This is a special case of a linear time invariant first
    order system

        a0 * dy/dt + a1 * y = b0 * du(t)/dt + b1 * u(t)

    The corresponding transferfunction is

               b0 * s^1 + b1 * s^0
        G(s) = -------------------
               a0 * s^1 + a1 * s^0

    .. note::

        We normalize the transfer function to `a0 = 1.` on instatiation.

    :param b: Numerator polynom.
    :param a: Denominator polynom.

    """
    def __init__(self, b, a):
        # Normalize transfer function.
        b = np.array(b) / a[0]
        a = np.array(a) / a[0]
        super(FirstOrder, self).__init__(b, a)

    @classmethod
    def from_ck(self, heat_capacity, thermal_conductivity):
        b = [0., 1. / heat_capacity]
        a = [1., thermal_conductivity / heat_capacity]
        return cls(b, a)

    @property
    def heat_capacity(self):
        return 1. / self.num[1]

    @property
    def thermal_conductivity(self):
        return self.den[1] / self.num[1]

    @classmethod
    def fit(cls, t, y, u):
        """Fits a first order heat capacity model.

        :param t: A sequence of timestamps.
        :param y: A sequence of temperatures.
        :param u: A sequence of heater power values.

        """
        yspline = interpolate.UnivariateSpline(t, y, s=0)
        uspline = interpolate.UnivariateSpline(t, u, s=0)

        ti = np.linspace(np.min(t), np.max(t), len(t))
        yi = yspline(ti)
        dyi = yspline.derivative(n=1)(ti)
        ui = uspline(ti)
        result = linalg.lstsq(np.hstack((yi[:,None], ui[:, None])) , dyi)[0]

        b = np.r_[0., result[1]]
        a = np.r_[1., - result[0]]

        return cls(b, a)
