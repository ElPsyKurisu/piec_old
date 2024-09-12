"""
Set's up the instrument class that all instruments will inherit basic functionlity from to be followed by sub classes (e.g. scope, wavegen)
"""

# Define a class
class Instrument:
    # Class attribute
    species = "Canis familiaris" #do we need any class attributes

    # Initializer / Instance attributes
    def __init__(self, name):
        self.name = name

    # Generic Methods all instruments should have
    def idn(self):
        """
        Queries the instrument for its ID

        """
        return self.query("*IDN?")


    def reset(self):
        """
        Resets the instrument to its default parameters
        """
        self.write("*RST")


    def initialize(self):
        """
        Resets the instrument and clears the registry
        """
        self.write("*RST")
        self.write("*CLS")

class Scope(Instrument):
    """
    Sub-class of Instrument to hold the general methods used by scopes
    """

    def setup(self, channel: str=1, voltage_range: str=16, voltage_offset: str=1.00, delay: str='100e-6',
          time_range: str='1e-3', autoscale=True):
        """
        Sets up the oscilliscope with the given paramaters. If autoscale is turned on it will ignore
        all other arguments and simply autoscale the instrument. Otherwise sample paramters are given
        as the default values. First the Program resets the instrument and after passing in desired parameters
        it sets the scope up for acquiring.

        args:
            self (pyvisa.resources.gpib.GPIBInstrument): SCOPE
            channel (str): Desired channel allowed values are 1,2,3,4
            voltage_range (str): The y scale of the oscilloscope, max is 40V, min is 8mV
            voltage_offset (str): The offset for the voltage in units of volts
            delay (str): The delay in units of s
            time_range (str): The x scale of the oscilloscope, min 2ns, max 50s
        """
        self.reset()
        if autoscale:
            self.write(":AUToscale")
        else:
            self.write("CHANel{}:RANGe {}".format(channel, voltage_range))
            self.write("CHANel{}:OFFSet {}".format(channel, voltage_offset))
            self.write("CHANel{}:TIMebase:RANGe {}".format(channel, time_range))
            self.write("CHANel{}:TIMebase:DELay {}".format(channel, delay))
        self.write(":ACQuire:TYPE NORMal")