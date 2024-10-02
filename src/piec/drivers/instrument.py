"""
Set's up the instrument class that all instruments will inherit basic functionlity from to be followed by sub classes (e.g. scope, wavegen)
"""
import numpy as np
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
    Sub-class of Instrument to hold the general methods used by scopes. For Now defaulted to DSOX3024a, but can always ovveride certain SCOPE functions
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

    def configure_timebase(self, time_base_type="MAIN", position="0.0",
                       reference="CENT", range=None, scale=None, vernier=False):
        """Configures the timebase of the oscilliscope. Adapted from EKPY program 'Configure Timebase (Basic)'
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
            self.write("TIM:MODE {}".format(time_base_type))
        if position is not None:
            self.write("TIM:POS {}".format(position))
        if range is not None:
            self.write("TIM:RANG {}".format(range))
        if reference is not None:
            self.write("TIM:REF {}".format(reference))
        if scale is not None:
            self.write("TIM:SCAL {}".format(scale))
        if vernier:
            self.write("TIM:VERN ON")
        else:
            self.write("TIM:VERN OFF")

    def configure_channel(self, channel: str='1', scale_mode=True, vertical_scale: str='5', vertical_range: str='40',
                              vertical_offset: str='0.0', coupling: str='DC', probe_attenuation: str='1.0', 
                              impedance: str='ONEM', enable_channel=True):
        """Sets up the voltage measurement on the desired channel with the desired paramaters. Taken from
        EKPY. 

        args:
            scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
            channel (str): Desired channel allowed values are 1,2,3,4
            scale_mode (boolean): Allows us to select between a vertical scale or range setting [see options below]
            vertical_scale (str): The vertical scale in units of v/div
            vertical_range (str): The verticale scale range min: 8mv, max: 40V
            vertical_offset (str): The offset for the vertical scale in units of volts
            coupling (str): 'AC' or 'DC' values allowed
            probe_attenuation (str): Multiplicative factor to attenuate signal to stil be able to read, max is most likely 10:1
            impedance (str): Configures if we are in high impedance mode or impedance match. Allowed factors are 'ONEM' for 1 M Ohm and 'FIFT' for 50 Ohm
            enable_channel (boolean): Enables the channel
        """
        if scale_mode:
            self.write("CHAN{}:SCAL {}".format(channel, vertical_scale))
        else:
            self.write("CHAN{}:RANG {}".format(channel, vertical_range))
        self.write("CHAN{}:OFFS {}".format(channel, vertical_offset))
        self.write("CHAN{}:COUP {}".format(channel, coupling))
        self.write("CHAN{}:PROB {}".format(channel, probe_attenuation))
        self.write("CHAN{}:IMP {}".format(channel, impedance))
        if enable_channel:
            self.write("CHAN{}:DISP ON".format(channel))
        else:
            self.write("CHAN{}:DISP OFF".format(channel))
    
    def configure_trigger_characteristics(self, type: str='EDGE', holdoff_time: str='4E-8', low_voltage_level: str='1',
                                      high_voltage_level: str='1', trigger_source: str='CHAN1', sweep: str='AUTO',
                                       enable_high_freq_filter=False, enable_noise_filter=False):
        """Configures the trigger characteristics Taken from LabVIEW. 'Configures the basic settings of the trigger.'
        args:
            scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
            type (str): Trigger type, accepted params are: [EDGE (Edge), GLIT (Glitch), PATT (Pattern), TV (TV), EBUR (Edge Burst), RUNT (Runt), NFC (Setup Hold), TRAN (Transition), SBUS1 (Serial Bus 1), SBUS2 (Serial Bus 2), USB (USB), DEL (Delay), OR (OR), NFC (Near Field Communication)]
            holdoff_time (str): Additional Delay in units of sec before re-arming trigger circuit
            low_voltage_level (str): The low trigger voltage level units of volts
            high_voltage_level (str): The high trigger voltage level units of volts
            trigger_source (str): Desired channel to trigger on allowed values are [CHAN1,CHAN2,CHAN3,CHAN4, EXT (there are more)]
            sweep (str): Allowed values are [AUTO (automatic), NORM (Normal)]
            enable_high_freq_filter (boolean): Toggles the high frequency filter
            enable_noise_filter (boolean): Toggles the noise filter
        """
        if enable_high_freq_filter:
            self.write(":TRIG:HFR ON")
        else:
            self.write(":TRIG:HFR OFF")
        self.write(":TRIG:HOLD {}".format(holdoff_time))
        self.write(":TRIG:LEV:HIGH {}, {}".format(high_voltage_level, trigger_source))
        self.write(":TRIG:LEV:LOW {}, {}".format(low_voltage_level, trigger_source))
        self.write(":TRIG:MODE {}".format(type))
        if enable_noise_filter:
            self.write(":TRIG:NREJ ON")
        else:
            self.write(":TRIG:NREJ OFF")
        self.write(":TRIG:SWE {}".format(sweep))

    def configure_trigger_edge(self, trigger_source: str='CHAN1', input_coupling: str='AC', edge_slope: str='POS', 
                           level: str='0', filter_type: str='OFF'):
        """Configures the trigger characteristics Taken from LabVIEW. 'Configures the basic settings of the trigger.'
        args:
            scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
            trigger_source (str): Desired channel/source to trigger on allowed values are: [CHAN1,CHAN2,CHAN3,CHAN4,DIG0,DIG1 (there are more)]
            input_coupling (str): Allowed values = [AC, DC, LFR (Low Frequency Coupling)]
            edge_slope (str): Allowed values = [POS, NEG, EITH (either), ALT (alternate)]
            level (str): Trigger level in volts
            filter_type (str): Allowed values = [OFF, LFR (High-pass filter), HFR (Low-pass filter)] Note: Low Frequency reject == High-pass
        """
        self.write(":TRIG:SOUR {}".format(trigger_source))
        self.write(":TRIG:COUP {}".format(input_coupling))
        self.write(":TRIG:LEV {}".format(level))
        self.write(":TRIG:REJ {}".format(filter_type))
        self.write(":TRIG:SLOP {}".format(edge_slope))

    def initiate(self):
        """
        Starts the measurement and acquires the channels currently 
        displayed. If no channels are displayed, all channels are 
        acquired.

        args:
            scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
        """
        self.write(":DIG")
        self.write("*CLS")
    
    def setup_wf(self, source: str='CHAN1', byte_order: str='MSBF', format: str='byte', points: str='1000', 
             points_mode: str='NORMal', unsigned: str='OFF'):
        """Sets up the waveform with averaging or not and of a specified format/count  
        args:
            scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
            source (str): Desired channel allowed values are [CHAN1, CHAN2, CHAN3, CHAN4, FUNC, SBUS1, etc]
            byte_order (str): Either MSBF (most significant byte first) or LSBF (least significant byte first)
            format (str): Format of data allowed args are [ASCii (floating point), WORD (16bit two-bytes), BYTE (8-bit)]
            points (str): Number of data points for the waveform to return allowed args are [100,250,500,1000] for NORM or up to [8000000] for MAX or RAW
            points_mode (str): Mode for points allowed args are [NORM (normal), MAX (maximum), RAW]
            unsigned (str): Allows to switch between unsigned and signed integers [OFF (signed), ON (unsigned)]
        """ 
        self.write(":WAVeform:SOURce {}".format(source))
        self.write(":WAVeform:BYTeorder {}".format(byte_order))
        self.write(":WAVeform:FORMat {}".format(format))
        self.write(":WAVeform:POINts:MODE {}".format(points_mode))
        self.write(":WAVeform:POINts {}".format(points))
        self.write(":WAVeform:UNSigned {}".format(unsigned))

    def query_wf(self, byte_order: str='MSBF', unsigned: str='OFF'):
        """Returns the specified channels waveform with averaging or not and of a specified format/count, call
        setup_wf first to intialize it correctly. This function only calls queries. First calls preamble to get
        data format. Then parses data and converts data to usable format.
        GET_PREAMBLE - The preamble block contains all of the current
        ' WAVEFORM settings. It is returned in the form <preamble_block><NL>
        ' where <preamble_block> is:
        ' FORMAT : int16-0= BYTE, 1 = WORD, 4 = ASCII.
        ' TYPE : int16-0= NORMAL, 1 = PEAK DETECT, 2 = AVERAGE
        ' POINTS : int32 - number of data points transferred.
        ' COUNT : int32 - 1 and is always 1.
        ' XINCREMENT : float64 - time difference between data points.
        ' XORIGIN : float64 - always the first data point in memory.
        ' XREFERENCE : int32 - specifies the data point associated with
        ' x-origin.
        ' YINCREMENT : float32 - voltage diff between data points.
        ' YORIGIN : float32 - value is the voltage at center screen.
        ' YREFERENCE : int32 - specifies the data point where y-origin
        ' occurs 
        args:
            scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
            byte_order (str): Either MSBF (most significant byte first) or LSBF (least significant byte first)
            unsigned (str): Allows to switch between unsigned and signed integers [OFF (signed), ON (unsigned)]

        returns:
            preamble_dict (dict) Dictionary with all params labeled. (MetaData)
            time (list): Python list with all the scaled time (x_data array)
            wfm (list): Python list with all the scaled y_values (y_data array) 
        """ 
        preamble = self.query(":WAVeform:PREamble?")
        preamble1 = preamble.split()
        preamble_list = preamble1[0].split(',')
        preamble_dict = {
        'format': np.int16(preamble_list[0]),
        'type': np.int16(preamble_list[1]),
        'points': np.int32(preamble_list[2]),
        'count': np.int32(preamble_list[3]),
        'x_increment': np.float64(preamble_list[4]),
        'x_origin': np.float64(preamble_list[5]),
        'x_reference': np.int32(preamble_list[6]),
        'y_increment': np.float32(preamble_list[7]),
        'y_origin': np.float32(preamble_list[8]),
        'y_reference': np.int32(preamble_list[9]),
        }
        if byte_order == 'MSBF':
            is_big_endian = True
        if byte_order == 'LSBF':
            is_big_endian = False
        if unsigned == 'OFF':
            is_unsigned = False
        if unsigned == 'ON':
            is_unsigned = True
        if preamble_dict["format"] == 0 and not is_unsigned:
            data = self.query_binary_values("WAVeform:DATA?", datatype='b', is_big_endian=is_big_endian)
        if preamble_dict["format"] == 0 and is_unsigned:
            data = self.query_binary_values("WAVeform:DATA?", datatype='B', is_big_endian=is_big_endian)
        if preamble_dict["format"] == 1 and not is_unsigned:
            data = self.query_binary_values("WAVeform:DATA?", datatype='h', is_big_endian=is_big_endian)
        if preamble_dict["format"] == 1 and is_unsigned:
            data = self.query_binary_values("WAVeform:DATA?", datatype='H', is_big_endian=is_big_endian)
        if preamble_dict["format"] == 4:
            data = self.query_ascii_values("WAVeform:DATA?")
        time = []
        wfm = []
        for t in range(preamble_dict["points"]):
            time.append((t* preamble_dict["x_increment"]) + preamble_dict["x_origin"])
        for d in data:
            wfm.append((d * preamble_dict["y_increment"]) + preamble_dict["y_origin"])
        return preamble_dict, time, wfm