#  -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import *
import time
from heatcapacity.fit import FirstOrder


class Simulation(object):
    """The Simulation object can be used if a real experiment is not available.

    :param model: An lti model used to simulate the temperature output.
    :param heater_resistance: A resistance in ohm used to calculate the voltage
        drop.
    :param noise_level: A sample taken from the standard normal distribution
        scaled by the `noise_level` is added to the simulated temperature output.

    E.g.::

        import heatcapacity as hc

        sim = hc.Simulation(
            hc.FirstOrder.from_ck(0.005, 0.002),
            heater_resistance=1e3,
            temperature_noise=0.1
        )
        sampling_time = 0.1
        pulse_sequence = [0.] * 60 * sampling_time + [1.] * 60 * sampling_time

        measurement = hc.PulsMeasurement(
            currentsource=sim, powermeter=sim, thermometer=sim,
            pulse=pulse_sequence, sampling_time=sampling_time)

        measurement.start()

    """
    def __init__(self, model, heater_resistance, noise_level):
        self.model = model
        self.current = 0.
        self.xout = None
        self.noise_level = noise_level

    @property
    def voltage(self):
        return self.resistance * self.voltage

    @property
    def temperature(self):
        """Simulates the temperature response to the current change."""
        t = time.time()
        tout, yout, xout = self.model.output([self.voltage * self.current], [t], self.state)
        self.state = xout
        assert len(yout) == 1
        return yout[0] + np.random.standart_normal() * self.noise_level
