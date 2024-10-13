"""
Set's up the instrument class that all instruments will inherit basic functionlity from to be followed by sub classes (e.g. scope, wavegen)
"""
from typing import Union
import numpy as np
from pyvisa import ResourceManager

# Define a class
class Instrument:
    # Class attribute
    species = "Canis familiaris" #do we need any class attributes

    # Initializer / Instance attributes
    def __init__(self, address):
        rm = ResourceManager()
        self.instrument = rm.open_resource(address) #comment out to debug without VISA connection

    def _debug(self, **args):
        """
        Debugging Function for _check_params not intended for actual code use, REQUIRES self.instrument above to be commented out
        """
        self._check_params(locals()['args']) #only need this here since i did **args

    # Generic Methods all instruments should have
    def idn(self):
        """
        Queries the instrument for its ID

        """
        return self.instrument.query("*IDN?")


    def reset(self):
        """
        Resets the instrument to its default parameters
        """
        self.instrument.write("*RST")

    def initialize(self):
        """
        Resets the instrument and clears the registry
        """
        self.instrument.write("*RST")
        self.instrument.write("*CLS")

    def check_errors(self):
        """
        Returns a list of errors or None if there are no errors
        Technically not an IEEE Mandated command but all instruments for our purposes should use this.
        With help from ChatGPT
        """
        errors = []
        while True:
            error = self.instrument.query('SYST:ERR?')
            if error.startswith('+0,'):
                break
            errors.append(error)
        if len(errors) == 0:
            errors = None
        return errors


    def print_specs(self):
        """
        Function that lists all class attributes for the instrument.
        """
        spec_dict = get_class_attributes_from_instance(self)
        for key in spec_dict:
            if spec_dict[key] != type(dict):
                print(key, ':', spec_dict[key])
            else:
                key_dict = getattr(self, key) #this is a dict that the key is the type e.g. list or dict
                key_dict_key = list(key_dict.keys())[0]
                key_dict_key_value = key_dict[key_dict_key]
                print(key, ':', key_dict_key_value)
            
    def _check_params(self, locals_dict):
        """
        Want to check class attributes and arguments from the function are in acceptable ranges. Uses .locals() to get all arguments and checks
        against all class attributes and ensures if they match the range is valid 
        """
        class_attributes = get_class_attributes_from_instance(self)
        keys_to_check = get_matching_keys(locals_dict, class_attributes)
        for key in keys_to_check:
            attribute_value = getattr(self, key) #allowed types are strings, tuples, lists, and dicts
            if attribute_value is None:
                print("Warning no range-checking defined for \033[1m{}\033[0m, skipping _check_params".format(key)) #makes bold text
                continue
            input_value = locals_dict[key]
            print(input_value, 'input value')
            if type(attribute_value) == tuple:
                if not is_value_between(input_value, attribute_value): #will error need to make jey values correct
                    exit_with_error("Error input value of \033[1m{}\033[0m for arg \033[1m{}\033[0m is out of acceptable Range \033[1m{}\033[0m".format(input_value, key, attribute_value))
            if type(attribute_value) == list:
                if not is_contained(input_value, attribute_value): #checks if the input value is in the allowed list
                    exit_with_error("Error input value of \033[1m{}\033[0m for arg \033[1m{}\033[0m is not in list of acceptable \033[1m{}\033[0m".format(input_value, key, attribute_value))
            if type(attribute_value) == dict:
                #need helper function here
                attribute_key = get_matching_keys(locals_dict, attribute_value) #this is the first key in the class attribute dict
                if len(attribute_key) != 1:
                    print("WARNING found {} keys instead of 1, skipping {} checking".format(len(attribute_key), key))
                else: #assumes input is range btw, since no other reason for using a dict i believe. WIll update if changes
                    local_value = locals_dict[attribute_key[0]] #this is the value
                    attribute_sub_dict = attribute_value[attribute_key[0]]
                    if not is_value_between(input_value, attribute_sub_dict[local_value]):
                        exit_with_error("Error input value of \033[1m{}\033[0m for arg \033[1m{}\033[0m is out of acceptable Range \033[1m{}\033[0m".format(input_value, attribute_key, attribute_sub_dict[local_value]))

class Scope(Instrument):
    """
    Sub-class of Instrument to hold the general methods used by scopes. For Now defaulted to DSOX3024a, but can always ovveride certain SCOPE functions
    """
    #Should be overriden
    voltage_range = None #entire screen range
    voltage_scale = None #units per division
    time_range = None   
    time_scale = None
    time_base_type = None

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
            time_range (str): The x scale of the oscilloscope, min 20ns, max 500s
        """
        self._check_params(locals())
        self.reset()
        if autoscale:
            self.instrument.write(":AUToscale")
        else:
            self.instrument.write("CHANel{}:RANGe {}".format(channel, voltage_range))
            self.instrument.write("CHANel{}:OFFSet {}".format(channel, voltage_offset))
            self.instrument.write("CHANel{}:TIMebase:RANGe {}".format(channel, time_range))
            self.instrument.write("CHANel{}:TIMebase:DELay {}".format(channel, delay))
        self.instrument.write(":ACQuire:TYPE NORMal")

    def configure_timebase(self, time_base_type="MAIN", position="0.0",
                       reference="CENT", time_range=None, time_scale=None, vernier=False):
        """Configures the timebase of the oscilliscope. Adapted from EKPY program 'Configure Timebase (Basic)'
        Should call initialize first.

        args:
            scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
            time_base_type (str): Allowed values are 'MAIN', 'WINDow', 'XY', and 'ROLL', note must use main for data acquisition
            position (str): The position in the scope, [0.0] is a good default This is actually the delay on the scope (moves in time right and left)
            time_range (str): The x range of the scope min is 20ns, max is 500s
            time_scale (str): The x scale of the scope in units of s/div min is 2ns, max is 50s
            vernier (boolean): Enables Vernier scale
        """
        self._check_params(locals())
        if time_base_type is not None:
            self.instrument.write("TIM:MODE {}".format(time_base_type))
        if position is not None:
            self.instrument.write("TIM:POS {}".format(position))
        if time_range is not None:
            self.instrument.write("TIM:RANG {}".format(time_range))
        if reference is not None:
            self.instrument.write("TIM:REF {}".format(reference))
        if time_scale is not None:
            self.instrument.write("TIM:SCAL {}".format(time_scale))
        if vernier:
            self.instrument.write("TIM:VERN ON")
        else:
            self.instrument.write("TIM:VERN OFF")

    def configure_channel(self, channel: str='1', scale_mode=True, voltage_scale: str='4', voltage_range: str='40',
                              voltage_offset: str='0.0', coupling: str='DC', probe_attenuation: str='1.0', 
                              impedance: str='ONEM', enable_channel=True):
        """Sets up the voltage measurement on the desired channel with the desired paramaters. Taken from
        EKPY. 

        args:
            scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
            channel (str): Desired channel allowed values are 1,2,3,4
            scale_mode (boolean): Allows us to select between a vertical scale or range setting [see options below]
            voltage_scale (str): The vertical scale in units of v/div
            voltage_range (str): The verticale scale range min: 8mv, max: 40V
            voltage_offset (str): The offset for the vertical scale in units of volts
            coupling (str): 'AC' or 'DC' values allowed
            probe_attenuation (str): Multiplicative factor to attenuate signal to stil be able to read, max is most likely 10:1
            impedance (str): Configures if we are in high impedance mode or impedance match. Allowed factors are 'ONEM' for 1 M Ohm and 'FIFT' for 50 Ohm
            enable_channel (boolean): Enables the channel
        """
        self._check_params(locals())
        if scale_mode:
            self.instrument.write("CHAN{}:SCAL {}".format(channel, voltage_scale))
        else:
            self.instrument.write("CHAN{}:RANG {}".format(channel, voltage_range))
        self.instrument.write("CHAN{}:OFFS {}".format(channel, voltage_offset))
        self.instrument.write("CHAN{}:COUP {}".format(channel, coupling))
        self.instrument.write("CHAN{}:PROB {}".format(channel, probe_attenuation))
        self.instrument.write("CHAN{}:IMP {}".format(channel, impedance))
        if enable_channel:
            self.instrument.write("CHAN{}:DISP ON".format(channel))
        else:
            self.instrument.write("CHAN{}:DISP OFF".format(channel))
    
    def configure_trigger_characteristics(self, type: str='EDGE', holdoff_time: str='4E-8', low_voltage_level: str='1',
                                      high_voltage_level: str='1', trigger_source: str='CHAN1', sweep: str='AUTO',
                                       enable_high_freq_filter=False, enable_noise_filter=False):
        """Configures the trigger characteristics Taken from EKPY. 'Configures the basic settings of the trigger.'
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
        self._check_params(locals())
        if enable_high_freq_filter:
            self.instrument.write(":TRIG:HFR ON")
        else:
            self.instrument.write(":TRIG:HFR OFF")
        self.instrument.write(":TRIG:HOLD {}".format(holdoff_time))
        self.instrument.write(":TRIG:LEV:HIGH {}, {}".format(high_voltage_level, trigger_source))
        self.instrument.write(":TRIG:LEV:LOW {}, {}".format(low_voltage_level, trigger_source))
        self.instrument.write(":TRIG:MODE {}".format(type))
        if enable_noise_filter:
            self.instrument.write(":TRIG:NREJ ON")
        else:
            self.instrument.write(":TRIG:NREJ OFF")
        self.instrument.write(":TRIG:SWE {}".format(sweep))

    def configure_trigger_edge(self, trigger_source: str='CHAN1', input_coupling: str='AC', edge_slope: str='POS', 
                           level: str='0', filter_type: str='OFF'):
        """Configures the trigger characteristics Taken from EKPY. 'Configures the basic settings of the trigger.'
        args:
            scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
            trigger_source (str): Desired channel/source to trigger on allowed values are: [CHAN1,CHAN2,CHAN3,CHAN4,DIG0,DIG1 (there are more)]
            input_coupling (str): Allowed values = [AC, DC, LFR (Low Frequency Coupling)]
            edge_slope (str): Allowed values = [POS, NEG, EITH (either), ALT (alternate)]
            level (str): Trigger level in volts
            filter_type (str): Allowed values = [OFF, LFR (High-pass filter), HFR (Low-pass filter)] Note: Low Frequency reject == High-pass
        """
        self._check_params(locals())
        self.instrument.write(":TRIG:SOUR {}".format(trigger_source))
        self.instrument.write(":TRIG:COUP {}".format(input_coupling))
        self.instrument.write(":TRIG:LEV {}".format(level))
        self.instrument.write(":TRIG:REJ {}".format(filter_type))
        self.instrument.write(":TRIG:SLOP {}".format(edge_slope))

    def initiate(self):
        """
        Starts the measurement and acquires the channels currently 
        displayed. If no channels are displayed, all channels are 
        acquired.

        args:
            scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
        """
        self.instrument.write(":DIG")
        self.instrument.write("*CLS")
    
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
        self._check_params(locals())
        self.instrument.write(":WAVeform:SOURce {}".format(source))
        self.instrument.write(":WAVeform:BYTeorder {}".format(byte_order))
        self.instrument.write(":WAVeform:FORMat {}".format(format))
        self.instrument.write(":WAVeform:POINts:MODE {}".format(points_mode))
        self.instrument.write(":WAVeform:POINts {}".format(points))
        self.instrument.write(":WAVeform:UNSigned {}".format(unsigned))

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
        self._check_params(locals())
        preamble = self.instrument.query(":WAVeform:PREamble?")
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
            data = self.instrument.query_binary_values("WAVeform:DATA?", datatype='b', is_big_endian=is_big_endian)
        if preamble_dict["format"] == 0 and is_unsigned:
            data = self.instrument.query_binary_values("WAVeform:DATA?", datatype='B', is_big_endian=is_big_endian)
        if preamble_dict["format"] == 1 and not is_unsigned:
            data = self.instrument.query_binary_values("WAVeform:DATA?", datatype='h', is_big_endian=is_big_endian)
        if preamble_dict["format"] == 1 and is_unsigned:
            data = self.instrument.query_binary_values("WAVeform:DATA?", datatype='H', is_big_endian=is_big_endian)
        if preamble_dict["format"] == 4:
            data = self.instrument.query_ascii_values("WAVeform:DATA?")
        time = []
        wfm = []
        for t in range(preamble_dict["points"]):
            time.append((t* preamble_dict["x_increment"]) + preamble_dict["x_origin"])
        for d in data:
            wfm.append((d * preamble_dict["y_increment"]) + preamble_dict["y_origin"])
        return preamble_dict, time, wfm


class Awg(Instrument):
    """
    Sub-class of Instrument to hold the general methods used by an awg. For Now defaulted to keysight81150a, but can always ovveride certain SCOPE functions
    """
    #Should be overriden
    channel = None
    voltage = None
    frequency = None
    func = None #might be useless since all awgs should have sin, squ, pulse etc
    slew_rate = None #1V/ns

    def configure_impedance(self, channel: str='1', source_impedance: str='50.0', load_impedance: str='50.0'):
        """
        This program configures the output and input impedance of the wavegen. Taken from EKPY.
        args:
            wavegen (pyvisa.resources.gpib.GPIBInstrument): Keysight 81150A
            channel (str): Desired Channel to configure accepted params are [1,2]
            source_impedance (str): The desired source impedance in units of Ohms, allowed args are [5, 50]
            load_impedance (str): The desired load impedance in units of Ohms, allowed args are [0.3 to 1E6]

        """
        self.instrument.write(":OUTP{}:IMP {}".format(channel, source_impedance))
        #wavegen.write(":OUTP{}:LOAD {}".format(channel, load_impedance)) Also valid for below
        self.instrument.write(":OUTP{}:IMP:EXT {}".format(channel, load_impedance))

    def configure_output_amplifier(self, channel: str='1', type: str='HIV'):
        """
        This program configures the output amplifier for eiither maximum bandwith or amplitude. Taken from EKPY.
        args:
            wavegen (pyvisa.resources.gpib.GPIBInstrument): Keysight 81150A
            channel (str): Desired Channel to configure accepted params are [1,2]
            type (str): Amplifier Type args = [HIV (MAximum Amplitude), HIB (Maximum Bandwith)]
        """
        self.instrument.write("OUTP{}:ROUT {}".format(channel, type))

    def configure_trigger(self, channel: str='1', trigger_source: str='IMM', mode: str='EDGE', slope: str='POS'):
        """
        This program configures the trigger. Taken from EKPY.
        args:
            wavegen (pyvisa.resources.gpib.GPIBInstrument): Keysight 81150A
            channel (str): Desired Channel to configure accepted params are [1,2]
            trigger_source (str): Trigger source allowed args = [IMM (immediate), INT2 (internal), EXT (external), MAN (software trigger)]
            mode (str): The type of triggering allowed args = [EDGE (edge), LEV (level)]
            slope (str): The slope of triggering allowed args = [POS (positive), NEG (negative), EIT (either)]
        """ 
        self.instrument.write(":ARM:SOUR{} {}".format(channel, trigger_source))
        self.instrument.write(":ARM:SENS{} {}".format(channel, mode))
        self.instrument.write(":ARM:SLOP {}".format(slope))

    def create_arb_wf_binary(self, data: Union[np.array, list], name: str='ARB1'):
        """
        NOTE: Dont think this works atm
        This program creates an arbitrary waveform within the limitations of the
        Keysight 81150A which has a limit of 2 - 524288 data points. In order to send data
        in accordance with the 488.2 block format which looks like #ABC, where '#' marks the start
        of the data flow and 'A' refers to the number of digits in the byte count, 'B' refers to the
        byte count and 'C' refers to the actual data in binary. The data is first scaled between
        -8191 to 8191 in accordance to our instrument. Adapted from EKPY (note their arrays
        contain 10,000 elements). 
        Note: Will NOT save waveform in non-volatile memory if all the user available slots are
        filled (There are 4 allowed at 1 time plus 1 in volatile memory).

        args:
            wavegen (pyvisa.resources.gpib.GPIBInstrument): Keysight 81150A
            data (ndarray or list): Data to be converted to wf
            name (str): Name of waveform, must start with A-Z
        """  
        #will want to include error handling in this one.
        data = np.array(data)
        scaled_data = scale_waveform_data(data)
        scaled_data = scaled_data.astype(np.int16)
        size_of_data = str(2*len(scaled_data)) #multiply by 2 to account for negative values?
        #want to send stuff accoprding to format whcih is #ABC
        a = len(size_of_data.encode('utf-8')) 
        b = size_of_data
        #c is the binary data to be passed
        c = scaled_data.tobytes()
        #i think im done?
        self.instrument.write(":FORM:BORD NORM")
        self.instrument.write(":DATA:DAC VOLATILE, #{}{}{}".format(a,b,c))
        self.instrument.write(":DATA:COPY {}, VOLATILE".format(name))

    def create_arb_wf(self, data, name=None):
        """
        This program creates an arbitrary waveform using the slow non binary format, see create_arbitrary_wf_binary for more info
        NOTE: Will NOT save waveform in non-volatile memory, unless a name is given.
        NOTE: Will NOT save waveform in non-volatile memory if all the user available slots are
        filled (There are 4 allowed at 1 time plus 1 in volatile memory).
        Also for 10k points it is quite slow, allow for like 3 seconds to send the data. Will need to rewrite the binary version
        if we want speed

        args:
            wavegen (pyvisa.resources.gpib.GPIBInstrument): Keysight 81150A
            data (ndarray or list): Data to be converted to wf
            name (str): Name of waveform, must start with A-Z
        """
        data_string = ""
        for i in range(len(data)):
            data_string += str(data[i]) +','
        data_string = data_string[:-1] #remove last comma
        self.instrument.write(":DATA VOLATILE, {}".format(data_string))
        if name is not None:
            self.instrument.write(":DATA:COPY {}, VOLATILE".format(name))



    #https://github.com/jeremyherbert/barbutils/blob/master/barbutils.py
    #upper frequnecy range is 120MHZ so do not go above that
    #maybe i can use this barb stuff to read the waveforms too...
    #finds avg max - min /2 can probably use githubn library to generate barb file then pass that

    def configure_arb_wf(self, channel: str='1', name='VOLATILE', voltage: str='1.0', offset: str='0.00', frequency: str='1000'):
        """
        This program configures arbitrary waveform already saved on the instrument. Taken from EKPY. 
        args:
            wavegen (pyvisa.resources.gpib.GPIBInstrument): Keysight 81150A
            channel (str): Desired Channel to configure accepted params are [1,2]
            name (str): The Arbitrary Waveform name as saved on the instrument, by default VOLATILE
            voltage (str): The V_pp of the waveform in volts
            offset (str): The voltage offset in units of volts
            frequency (str): the frequency in units of Hz for the arbitrary waveform
        """
        self.instrument.write(":FUNC{}:USER {}".format(channel, name)) #this had an error in it
        self.instrument.write(":FUNC{} USER".format(channel)) #this was put together like ":FUNC{}:USER {}:FUNC{} USER" I feel like I dont need both of these
        self.instrument.write(":VOLT{} {}".format(channel, voltage))
        self.instrument.write(":FREQ{} {}".format(channel, frequency))
        self.instrument.write(":VOLT{}:OFFS {}".format(channel, offset))  


    def output_enable(self, channel: str='1', on=True):
        """
        This program toggles the selected output. Taken from EKPY. 
        args:
            wavegen (pyvisa.resources.gpib.GPIBInstrument): Keysight 81150A
            channel (str): Desired Channel to configure accepted params are [1,2]
            on (boolean): True for on, False for off
        """
        if on:
            self.instrument.write(":OUTP{} ON".format(channel))
        else:
            self.instrument.write(":OUTP{} OFF".format(channel))

    def send_software_trigger(self):
        """
        This program sends the software trigger. Taken from EKPY. 
        args:
            wavegen (pyvisa.resources.gpib.GPIBInstrument): Keysight 81150A
        """
        self.instrument.write(":TRIG")

    def stop(self):
        """Stop the awg.

        args:
            wavegen (pyvisa.resources.ENET-Serial INSTR): Keysight 81150A
        """
        self.output_enable('1', False) #should change to take into account channels available from class attributes
        self.output_enable('2', False)

    def set_output_wf(self, channel: str='1', func='sine', frequency='1e3', voltage='1', offset='0', duty_cycle='50', num_cycles=None):
        """
        Decides what built-in wf to send - by default sin

        args:
            wavegen (pyvisa.resources.ENET-Serial INSTR): Keysight 81150A
            channel (str): Desired Channel to configure accepted params are [1,2]
            func (str): Desired output function, allowed args are [SIN (sine), SQU (square), RAMP, PULSe, NOISe, DC, USER (arb)]
            frequency (str): frequency in Hz (have not added suffix funcitonaility yet)
            voltage (str): The V_pp of the waveform in volts
            offset (str): DC offset for waveform in volts
            duty_cycle (str): duty_cycle defined as 100* pulse_width / Period ranges from 0-100, (cant actually do 0 or 100 but in between is fine)
            num_cycles (str): number of cycles by default set to None which means continous

        """
        self._check_params(locals())
        self.instrument.write(":SOUR:FUNC{} {}".format(channel, func)) 
        self.instrument.write(":SOUR:FREQ{} {}".format(channel, frequency))
        self.instrument.write(":VOLT{}:OFFS {}".format(channel, offset))
        self.instrument.write(":VOLT{} {}".format(channel, voltage))
        if func.lower() == 'squ' or func.lower() == 'square':
            self.instrument.write(":SOUR:FUNC{}:DCYC {}".format(channel, duty_cycle)) #DOES NOT WORK, will need to fix later
        if num_cycles is not None:
            self.instrument.write(":NCYCles{}".format(num_cycles))
        if func.lower() == 'pulse' or func.lower() == 'puls':
            self.instrument.write(":SOUR:FUNC{}:PULS:DCYC {}PCT".format(channel, duty_cycle))

        
    def couple_channels(self):
        """
        Couples the channel params so Channel 1 and 2 are identical, not sure how well the outputs will sync. 
        Convention is to make changes to channel 1 now that will affect channel 2

        args:
            wavegen (pyvisa.resources.ENET-Serial INSTR): Keysight 81150A
            
        """
        self.instrument.write(":TRACK:CHAN1 ON")


"""
Helper Functions Below
"""

def is_contained(value, lst):
    """
    Helper Function that checks if a string is contained within a list and ignores case sensitivity
    """
    my_string = value.lower()
    my_list = [item.lower() for item in lst]
    return my_string in my_list


def is_value_between(value, num_tuple):
    """
    Helper function that checks if the value is between allowed ranges, taken with help from ChatGPT
    """
    if type(value) is str:
        value = float(value)
    if len(num_tuple) != 2:
        raise ValueError("Tuple must contain exactly two numbers")
    return num_tuple[0] <= value <= num_tuple[1]


def get_matching_keys(dict1, dict2):
    """ 
    Find the intersection of keys from both dictionaries, taken from ChatGPT
    """
    matching_keys = set(dict1.keys()).intersection(dict2.keys())
    return list(matching_keys)

def get_class_attributes_from_instance(instance):
    """
    Helper Function to get the class attributes from an instance (calls self) with help from ChatGPT
    """
    cls = instance.__class__
    attributes = {}
    for base in cls.__mro__:
        attributes.update({attr: getattr(base, attr) for attr in base.__dict__ if not callable(getattr(base, attr)) and not attr.startswith("__")})
    return attributes

'''
Helper functions for awg class:
'''

def scale_waveform_data(data: np.array) -> np.array:
    '''
    Scales the data between -1 and 1 then multiplies by instrument specific
    scaling factor (8191 for ours) 
    NOTE THIS MAY NOT ACTUALLY WORK, AS YOU CAN JUST PASS THE DATA DIRECTLY AND SHOULD BE FROM -1 TO 1
    '''
    normalized = 2*(data - np.min(data))/np.ptp(data) - 1
    return normalized * 8191

"""
Error handling: maybe make a seperate python file to take care of error handling 

Also good idea to add option to suppress warnings, aka no print statements instead call warning function that has param that can be suppressed
"""

def exit_with_error(msg):
    """
    Function to raise error message that provides faster feedback
    """
    raise ValueError(msg)
