#  -*- coding: utf-8 -*-
"""

::

    from slave.transport import LinuxGpib
    import heatcapacity as hc

    # We use a Keithley model 6221 as current source,
    source = hc.K6221CurrentSource(LinuxGpib(8))

    # a Keithley model 2182A Nanovoltmeter to measure the voltage drop at the
    # heater,
    powermeter = hc.K2182Powermeter(LinuxGpib(9))

    #and a lakeshore model 370 to determine the platform temperature.
    thermometer = hc.LS370Thermometer(LinuxGpib(10))

    # We sample at a rate of 0.1 s and use a step pulse with 1 uA to excite the
    # system.
    sampling_time = 0.1
    pulse_sequence = [0.] * 60 * sampling_time + [1.] * 60 * sampling_time

    # The PulseMeasurement object is used to acquire the data.
    measurement = hc.PulseMeasurement(currentsource, powermeter, thermometer,
                                      pulse, sampling_time)
    timestamp, power, temperature = measurement.start()

    # We fit a first order model to get the heat capacity.
    model = hc.FirstOrderModel.fit(timestamp, temperature, power)

    print('C {}; K {}'.format(model.heat_capacity, model.thermal_conductivity))


"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import *
__version__ = '0.1.0'

from heatcapacity.measure import *
from heatcapacity.fit import *
