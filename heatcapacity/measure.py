#  -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import *
import time
import contextlib

import numpy as np


class Measurement(object):
    """Abstract base class defining the heat capacity measurement interface.

    :param currentsource: An object implementing the :class:`CurrentSource`
        interface.
    :param powermeter: An object implementing the :class:`Powermeter` interface.
    :param thermometer: An object implementing the :class:`Thermometer`
        interface.

    """
    def __init__(self, currentsource, powermeter, thermometer):
        self.currentsource = currentsource
        self.powermeter = powermeter
        self.thermometer = thermometer

    def start(self):
        """Starts the heat capacity measurement."""
        raise NotImplementedError()

    def measure(self):
        """Measures the time, heater power and platform temperature."""
        timestamp = time.time()
        current = self.currentsource.current
        heater_voltage = self.powermeter.voltage
        temperature = self.thermometer.temperature
        return timestamp, current * heater_voltage, temperature


class CurrentSource(object):
    """Abstract base class defining the current source interface."""
    @property
    def current(self):
        raise NotImplementedError()

    @current.setter
    def current(self, value):
        raise NotImplementedError()


class Powermeter(object):
    """Abstract base class defining the powermeter interface."""
    @property
    def voltage(self):
        raise NotImplementedError()


class Thermometer(object):
    """Abstract base class defining the thermometer interface."""
    @property
    def temperature(self):
        raise NotImplementedError()


class PulseMeasurement(Measurement):
    """A heat capacity measurement using a predefined pulse sequence.

    :param currentsource: An object implementing the :class:`CurrentSource`
        interface.
    :param powermeter: An object implementing the :class:`Powermeter` interface.
    :param thermometer: An object implementing the :class:`Thermometer`
        interface.
    :param pulse: A sequence of current values.
    :param sampling_time: The sampling time.

    """
    def __init__(self, currentsource, powermeter, thermometer, pulse, sampling_time):
        super(PulseMeasurement, self).__init__(currentsource, powermeter, thermometer)
        self.pulse = pulse
        self.sampling_time = sampling_time

    def start(self):
        """Starts the heat capacity measurement."""
        data = []
        for current in self.pulse:
            with sampling(self.sampling_time):
                self.currentsource.current = current
                data.append(self.measure)

        timestamp, power, temperature = zip(*data)
        return timestamp, power, temperature


class AdaptiveStep(Measurement):
    def __init__(self, currentsource, powermeter, thermometer, duration, max_current, min_current=0., window=None, sampling=0.1):
        super(AdaptiveStep, self).__init__(currentsource, powermeter, thermometer)
        self.duration = duration
        self.max_current = max_current
        self.min_current = min_current
        self.sampling = sampling
        self.deriv_threshold = 1
        
        if window is None:
            window = duration / sampling / 5
            self.window = window + 1 if window % 2 == 0 else window
        else:
            self.window = window
            
        self.order = 2
        
    def start(self, verbose=False):
        data = []
        derivative = []

        input = audiolazy.ControlStream(0.)
        deriv_filt = savitzky_golay(self.window, self.order, deriv=1., sampling=self.sampling)(input)
        
        # measure steady state
        start = time.time()
        self.currentsource.current = self.min_current
        while time.time() - start < self.duration:
            with sampling(self.sampling):
                timestamp, power, temperature = self.measure()
                data.append((timestamp, power, temperature))
                # Update derivative filter
                input.value = temperature / power if power else temperature
                derivative.append(deriv_filt.take())
        
        #measure response to heat pulse
        start = time.time()
        self.currentsource.current = self.max_current
        while (time.time() - start < self.duration) or (np.abs(derivative[-1]) > self.deriv_threshold):
            with sampling(self.sampling):
                timestamp, power, temperature = self.measure()
                data.append((timestamp, power, temperature))
                # Update derivative filter
                input.value = temperature / power if power else temperature
                derivative.append(deriv_filt.take())
                
        #measure decay for the same time
        duration = time.time() - start
        start = time.time()
        self.currentsource.current = self.min_current
        while time.time() - start < duration:
            with sampling(self.sampling):
                timestamp, power, temperature = self.measure()
                data.append((timestamp, power, temperature))
                # Update derivative filter
                input.value = temperature / power if power else temperature
                derivative.append(deriv_filt.take())

        timestamp, power, temperature = zip(*data)
        if verbose:
            return timestamp, power, temperature, derivative
        return timestamp, power, temperature


import audiolazy
from scipy import signal

def savitzky_golay(window, order, deriv=1, sampling=1.):
    return audiolazy.ZFilter(numerator=signal.savgol_coeffs(window, order, deriv=deriv, delta=sampling, use='conv').tolist())

@contextlib.contextmanager
def sampling(step, sleep_ratio=0.01):
    assert step > 0
    
    start = time.time()
    yield
    while (time.time() - start) < step:
        time.sleep(step * sleep_ratio)