'''
This is for the KEYSIGHT DSOX3024a Oscilloscope and requires the KEYSIGHT I/O Libraries to function.
'''
import numpy as np
import time
from instrument import Scope
#yes

class DSOX3024a(Scope):
    """
    Specific Class for this exact model of scope: Keysight DSOX3024a
    """
    #add class attributes here, like max y range etc
    voltage_range = {'range':(8e-3, 40)} #voltage range
    voltage_scale = {'range':(8e-4, 4)} #TO UPDATE WHEN I GET IN LAB WITH CORRECT VALUES
    time_range = {'range':(2e-8, 500)}
    time_scale = {'range':(2e-9, 50)}
    time_base_type = {'list': ['MAIN', 'WINDow', 'WIND', 'XY', 'ROLL']} #added WIND so either WIND or WINDOW is allowed

    def __class_specific(self):
        """
        Place to define instrument specific stuff. Ideally never needed if Parent class is robust enough and instead
        we just define class attributes as above
        """
        return None




