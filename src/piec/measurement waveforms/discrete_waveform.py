import numpy as np
import time

class DiscreteWaveform:
    def __init__(self, awg_address, osc_address, trigger_amp=1):
        """
        General waveform parent class.
        
        :param awg_address: VISA address of the Arbitrary Waveform Generator
        :param osc_address: VISA address of the Oscilloscope
        :param trigger_amp: V of trigger pulse in V, scope trigger level will be trigger/2
        """
        self.awg = TektronixAWG(awg_address)
        self.osc = AgilentOscilloscope(osc_address)
        self.trigger_amp = trigger_amp
        self.data = None

    def configure_trigger(self):
        self.awg.channel1.function_shape = 'pulse'
        self.awg.channel1.amplitude = trigger_amp  # 1V pulse amplitude by default
        self.awg.channel1.pulse_width = 1  # Pulse width in seconds

    def configure_oscilloscope(self):
        """
        Configures the Oscilloscope to capture the waveform.
        """
        self.osc.time_scale = 1 / (10 * self.frequency)  # Adjust time scale based on wave period
        self.osc.trigger_level = self.offset  # Set trigger level to waveform offset
        print("Oscilloscope configured.")

    def capture_waveform(self):
        """
        Captures the waveform data from the oscilloscope.
        """
        print(f"Capturing waveform for {self.n_cycles} seconds...")
        time.sleep(self.n_cycles)  # Wait for the oscilloscope to capture the waveform
        self.data = self.osc.data  # Retrieve the data from the oscilloscope
        print("Waveform captured.")

    def save_waveform(self, filename):
        """
        Saves the captured waveform data to a file.
        
        :param filename: Path to the file where the waveform will be saved (CSV format).
        """
        if self.data is not None:
            np.savetxt(filename, self.data, delimiter=',', header='Time, Voltage', comments='')
            print(f"Waveform data saved to {filename}")
        else:
            print("No data to save. Capture the waveform first.")

    def run_experiment(self, save_path="waveform.csv"):
        """
        Runs the entire experiment by configuring the AWG, capturing the waveform, and saving the data.
        
        :param save_path: Path where the waveform will be saved (default: "waveform.csv")
        """
        self.configure_awg()
        self.configure_trigger()
        self.configure_oscilloscope()
        self.capture_waveform()
        self.save_waveform(save_path)

class HysteresisLoop(DiscreteWaveform):
    def __init__(self, frequency=1000, amplitude=1, offset=0, n_cycles=2):
        """
        Initializes the HysteresisLoop class.
        
        :param frequency: Frequency of the triangle wave (in Hz)
        :param amplitude: Peak amplitude of the triangle wave (in Volts)
        :param offset: Offset of the triangle wave (in Volts)
        :param n_cycles: number of triangle cycles to run
        """
        self.frequency = frequency
        self.amplitude = amplitude
        self.offset = offset
        self.n_cycles = n_cycles

    def configure_awg(self):
        """
        Configures the Arbitrary Waveform Generator (AWG) to output a triangle wave.
        """
        # Set the AWG to generate a triangle wave
        ###########################################
        #INCOMPLETE
        ###########################################
        self.awg.function_shape = 'triangle'
        self.awg.frequency = self.frequency
        self.awg.amplitude = self.amplitude
        self.awg.offset = self.offset
        self.awg.output = True
        print("AWG configured for a triangle wave.")

class PUNDPulse(DiscreteWaveform):
    def __init__(self, reset_amp=1, reset_width=1e-3, reset_delay=1e-3, p_u_amp=1, p_u_width=1e-3, p_u_delay=1e-3, offset=0,):
        """
        Initializes the HysteresisLoop class.
        
        :param reset_amp: amplitude of reset pulse, polarity is polarity of P and u pulses x(-1) (in Volts)
        :param reset_width: width of reset pulse (in s)
        :param reset_delay: delay between reset pulse and p pulse (in s)
        :param p_u_amp: amplitude of p and u pulses, polarity is polarity of P and u pulses x(-1) (in Volts)
        :param p_u_width: width of p and u pulses (in s)
        :param p_u_delay: delay between p pulse and u pulse (in s)
        :param offset: Offset of the PUND waveform (in Volts)
        """
        self.frequency = frequency
        self.amplitude = amplitude
        self.offset = offset
        self.n_cycles = n_cycles

    def configure_awg(self):
        """
        Configures the Arbitrary Waveform Generator (AWG) to output a triangle wave.
        """
        # Set the AWG to generate a triangle wave
        ###########################################
        #WRITE
        ###########################################
        print("AWG configured for a PUND pulse.")

    

# Example usage:
# experiment = HysteresisLoop(awg_address="GPIB::10::INSTR", osc_address="GPIB::1::INSTR")
# experiment.run_experiment(save_path="triangle_wave_data.csv")

