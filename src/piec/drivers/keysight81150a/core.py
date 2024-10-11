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
    #correct syntax is tuple for ranges, list for limited amount, and dictionaries for nested things...
    channel = {'list': ['1', '2']} #allowable channels
    voltage = {'range':(8e-3, 40)}
    frequency = {'nested': {'sine': (1e-6, 240e6), 'square': (1e-6, 120e6), 'ramp': (1e-6, 5e6), 'pulse': (1e-6, 120e6), 'pattern': (1e-6, 120e6), 'arb': (1e-6, 120e6)}} #note pattern is 10e6 max freq for external pattern
    func = {'list': ['sine', 'square', 'ramp', 'pulse', 'pattern', 'arb']} #might be useless since all awgs should have sin, squ, pulse etc maybe not include arb? idk
    slew_rate = '1V/ns' #1V/ns these are the units, currently just to know

    def __class_specific(self):
        """
        Place to define instrument specific stuff. Ideally never needed if Parent class is robust enough and instead
        we just define class attributes as above
        """
        return None
