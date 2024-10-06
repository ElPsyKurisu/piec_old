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
    voltage_range = (0.008, 40) #voltage range
    time_range = (2e-9, 50)

    def __class_specific(self):
        """
        Place to define instrument specific stuff. Ideally Never needed if Parent class is robust enough and instead
        we just define class attributes as above
        """
        return None




