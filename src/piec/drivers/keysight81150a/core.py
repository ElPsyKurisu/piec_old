'''
This is for the KEYSIGHT 81150A Arbitrary Waveform Generator and requires the KEYSIGHT I/O Libraries to function. check if true
'''
import numpy as np
import time
from ..instrument import Awg
#yes

class Keysight81150a(Awg):
    """
    Specific Class for this exact model of awg: Keysight 81150A
    """
    #add class attributes here, like max y range etc
    channel = {'list': ['1', '2']} #allowable channels
    voltage = {'range':(8e-3, 40)}
    frequency = {'range': {'sine': (1e-6, 240e6), 'square': (1e-6, 120e6), 'ramp': (1e-6, 5e6), 'pulse': (1e-6, 120e6), 'pattern': (1e-6, 120e6), 'arb': (1e-6, 120e6)}} #note pattern is 10e6 max freq for external pattern
    func = {'list': ['sine', 'square', 'ramp', 'pulse', 'pattern', 'arb']} #might be useless since all awgs should have sin, squ, pulse etc
    slew_rate = None #1V/ns
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

    def setup(self, channel: str = 1, voltage_range: str = 16, voltage_offset: str = 1, delay: str = '100e-6', time_range: str = '1e-3', autoscale=True):
        """
        Override default params here by ovverriding class Scope funtions
        """
        return super().setup(channel, voltage_range, voltage_offset, delay, time_range, autoscale)