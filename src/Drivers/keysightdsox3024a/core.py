'''
This is for the KEYSIGHT DSOX3024a Oscilloscope and requires the KEYSIGHT I/O Libraries to function.
'''
import numpy as np
import time
from instrument import Scope


class DSOX3024a(Scope):
    """
    Specific Class for this exact model of scope: Keysight DSOX3024a
    """
    def configure_timebase(scope, time_base_type="MAIN", position="0.0",
                        reference="CENT", range=None, scale=None, vernier=False):
        """Configures the timebase of the oscilliscope. Adapted from LabVIEW program 'Configure Timebase (Basic)'
        Should call initialize first.

        args:
            scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
            time_base_type (str): Allowed values are 'MAIN', 'WINDow', 'XY', and 'ROLL', note must use main for data acquisition
            position (str): The position in the scope, [0.0] is a good default This is actually the delay on the scope (moves in time right and left)
            range (str): The x range of the scope min is 20ns, max is 500s
            scale (str): The x scale of the scope in units of s/div min is 2ns, max is 50s
            vernier (boolean): Enables Vernier scale
        """
        if time_base_type is not None:
            scope.write("TIM:MODE {}".format(time_base_type))
        if position is not None:
            scope.write("TIM:POS {}".format(position))
        if range is not None:
            scope.write("TIM:RANG {}".format(range))
        if reference is not None:
            scope.write("TIM:REF {}".format(reference))
        if scale is not None:
            scope.write("TIM:SCAL {}".format(scale))
        if vernier:
            scope.write("TIM:VERN ON")
        else:
            scope.write("TIM:VERN OFF")


