#  -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import *
import time

import numpy as np
from scipy import signal
import audiolazy


class Simulation(object):
    """The Simulation object can be used if a real experiment is not available.

    :param model: An lti model used to simulate the temperature output.
    :param sampling: The sampling time.
    :param heater_resistance: A resistance in ohm used to calculate the voltage
        drop.
    :param sigma: The standart deviation of tjhe gaussian noise added to the simulated temperature
    

    E.g.::

        import heatcapacity as hc

        sampling_time = 0.1
        sim = hc.Simulation(
            hc.FirstOrder.from_ck(0.004, 0.002),
            sampling=sampling_time,
            heater_resistance=1e3,
            sigma=1.
        )
        
        pulse_sequence = [0.] * 60 * sampling_time + [0.001] * 60 * sampling_time

        measurement = hc.PulsMeasurement(
            currentsource=sim, powermeter=sim, thermometer=sim,
            pulse=pulse_sequence, sampling_time=sampling_time)

        measurement.start()

    """
    def __init__(self, model, sampling, heater_resistance, sigma, ):
        self.heater_resistance = heater_resistance
        
        self.power = audiolazy.ControlStream(0.)
        self.current = 0.
        
        # convert model to discrete representation
        num, den, dt = signal.cont2discrete((model.num, model.den), sampling)
        model = audiolazy.ZFilter(list(num.flatten()), list(den.flatten()))
        self.model = model(self.power) + audiolazy.gauss_noise(sigma=sigma)

    @property
    def current(self):
        return self._current
    
    @current.setter
    def current(self, value):
        self._current = value
        self.power.value = self.voltage * self.current
        
    @property
    def voltage(self):
        return self.heater_resistance * self.current

    @property
    def temperature(self):
        """Simulates the temperature response to the current change."""
        return self.model.take()