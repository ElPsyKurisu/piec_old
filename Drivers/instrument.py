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