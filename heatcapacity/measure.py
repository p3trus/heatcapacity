#  -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import *
import time


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
            start = time.time()
            self.currentsource.current = current
            data.append(self.measure)
            while (time.time() - start) < self.sampling_time:
                time.sleep(self.sampling_time / 100.)
        timestamp, power, temperature = zip(*data)
        return timestamp, power, temperature

