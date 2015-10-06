#  -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import *
import time

import numpy as np
from scipy import signal

class Simulation(object):
    """The Simulation object can be used if a real experiment is not available.

    :param model: An lti model used to simulate the temperature output.
    :param heater_resistance: A resistance in ohm used to calculate the voltage
        drop.
    :param noise_scale: A sample taken from the standard normal distribution
        scaled by the `noise_scale` is added to the simulated temperature output.
    

    E.g.::

        import heatcapacity as hc

        sim = hc.Simulation(
            hc.FirstOrder.from_ck(0.005, 0.002),
            heater_resistance=1e3,
            noise_scale=0.1
        )
        sampling_time = 0.1
        pulse_sequence = [0.] * 60 * sampling_time + [1.] * 60 * sampling_time

        measurement = hc.PulsMeasurement(
            currentsource=sim, powermeter=sim, thermometer=sim,
            pulse=pulse_sequence, sampling_time=sampling_time)

        measurement.start()

    """
    def __init__(self, model, heater_resistance, noise_scale, sampling_time, x0=0.):
        # convert model to discrete statespace representation
        self.model = signal.cont2discrete(signal.tf2ss(model.num, model.den), sampling_time)

        self.heater_resistance = heater_resistance
        self.noise_scale = noise_scale
        self.x0 = x0

        self.current = 0.
        self._state = None

    @property
    def voltage(self):
        return self.heater_resistance * self.current

    @property
    def temperature(self):
        """Simulates the temperature response to the current change."""
        if self._state is None:
            u = self.voltage * self.current
            self._state = u, self.x0
        u0, x0 = self._state
        uin = [u0, self.voltage * self.current]
        tout, yout, xout = signal.dlsim(self.model, uin, x0=x0)

        # Update state
        self._state = uin[-1], xout[-1]

        return yout[-1] + np.random.normal(scale=self.noise_scale)