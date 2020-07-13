try:
    import numpy as np
    import wave
    from scipy.io import wavfile
    from pyaudio import PyAudio, paInt16
except ImportError as e: # most likely a ModuleNotFoundError
    raise Exception(f'Could not import a module: {e}.')

class SoundData:
    def __init__(self, chunk=1024, rate=44100):
        '''
        Initialize a SoundData object.

        Args:
            chunk (int) : number of samples grouped together
                          default: 1024
            rate  (int) : sampling frequency in Hz
                          default: 44100
        '''
        self.chunk  = chunk
        self.rate   = rate
        self.buffer = None
        self.audio_stream = PyAudio().open(format=paInt16, # Create an audio stream object from the microphone using PyAudio
                                           channels=1,
                                           rate=rate,
                                           input=True,
                                           frames_per_buffer=chunk)

    def _write_stream_to_file(self, filename, data):
        '''
        Write contents of data to a Wave file.

        Args:
            filename  (str) : name of Wave file to be written to
            data     (list) : mono audio signal
        '''
        wave_file = wave.open(f'./assets/{filename}.wav', 'wb') # Open the Wave file in binary write mode
        wave_file.setnchannels(1) # Set details of the data being written
        wave_file.setsampwidth(PyAudio().get_sample_size(paInt16))
        wave_file.setframerate(self.rate)
        wave_file.writeframes(b''.join(data)) # Convert the list into a binary string and (over)write to the Wave file
        wave_file.close()

    def _framing(self, data):
        '''
        Transform audio signal into a series of overlapping frames.
        A frame (sample) is the amplitude at a point in time.

        Args:
            data         (list) : mono audio signal

        Returns:
            frames       (list) : all the frames
            frame_length  (int) : length of each frame
        '''
        frame_length     = int(.025 * self.rate) # Frame length = (window length) * (rate), .025 secs chosen arbitrarily
        frame_step       = int(.01  * self.rate) # Used to convert from seconds to samples, .01 secs between windows chosen arbitrarily
        signal_length    = len(data)
        number_of_frames = int(np.ceil(abs(signal_length-frame_length)/frame_step)) # Check there is at least one frame

        # Find indices
        index_a = np.tile(np.arange(0, frame_length), (number_of_frames, 1)) # numpy.arange(start,stop,step) returns evenly spaced values between start & stop
                                                                       # numpy.tile(array, repeats) constructs an array by repeating the given array in each given axis (repeats)
        index_b = np.tile(np.arange(0, number_of_frames*frame_step, frame_step), (frame_length, 1))
        index_b = np.transpose(index_b) # Rearrange the array so rows become columns and colums become rows
        indices = index_a + index_b

        # Pad out the signal to ensure the frames have at least the same length as the indices array
        padding_amount = number_of_frames * frame_step + frame_length
        padding        = np.zeros((padding_amount-signal_length)) # Creates a numpy array filled entirely of zeros
        padded_buffer  = np.append(data, padding) # Merges two arrays into one

        frames = padded_buffer[indices.astype(np.int32, copy=False)] # .astype(dtype, copy=False) changes the type of the indices array to int32
        return frames, frame_length

    def _get_dominant_frequency(self, frame):
        '''
        Find the dominant frequency of a single frame.

        Args:
            frame (numpy.ndarray) : amplitude information at a point in time
        
        Returns:
                          (float) : dominant frequency in Hz
        '''
        nfft = 2**14 # Fast fourier transform points to be calculated
        fourier_transform = np.fft.rfft(frame, nfft) # Perform a fast fourier transform on a real input

        magnitude_spectrum = (1/nfft) * abs(fourier_transform)
        power_spectrum = (1/nfft)**2 * magnitude_spectrum**2

        frequencies = np.fft.fftfreq(len(power_spectrum), 1/self.rate) # Gives the frequencies associated with the coefficients: .fftfreq(window_length,sampling_spacing) where sampling_spacing is the inverse of sampling rate
        frequencies = (frequencies[np.where(frequencies >= 0)] // 2) + 1 # Filter out negative frequencies and return the floor division of 2 for each frequency. Finally, add 1 to each frequency
         
        power_spectrum = power_spectrum[:len(frequencies)] # Take only the first half of the spectra as only the first part contains useful data
        maxiumum_index = np.argmax(power_spectrum) # .argmax() returns the maximum values along an axis

        return frequencies[maxiumum_index] # Convert the dominant frequency to Hz
        
        
    def stream(self, time=.1):
        '''
        Update audio stream buffer.
        
        Args:
            time (float) : length of audio stream buffer in seconds
                           default: 0.1
        '''
        # To record (time) seconds into the buffer, we must take (rate)*(time) samples.
        # In each iteration (chunk) samples are taken, so we must loop (rate)*(time)/(chunk) times.
        buffer_hex = [self.audio_stream.read(self.chunk) for i in range(int(self.rate/self.chunk*time))]
        self._write_stream_to_file('buffer', buffer_hex)
        self.rate, self.buffer = wavfile.read('./assets/buffer.wav')

    def get_dominant_frequencies(self):
        '''
        Analyse the buffer data to find the dominant frequencies.

        Returns:
            dominant_frequencies (list) : list of the dominant frequencies identified
        '''
        # Perform framing on the signal
        frames, frame_length = self._framing(self.buffer)
        # Perform Hamming window function on the frames
        windows = frames * np.hamming(frame_length) # w(n) = .54 - .46*cos((2*(pi)*n)/(M-1)) , 0 <= n <= M-1 where M = number of points in the output window

        dominant_frequencies = np.array([self._get_dominant_frequency(window) for window in windows]) # Find the dominant frequency for each frame
        dominant_frequencies = np.round(dominant_frequencies, 3) # Round to three decimal places
        dominant_frequencies = np.unique(dominant_frequencies) # Remove all duplicate values

        return dominant_frequencies

    def get_note_from_frequency(self, notes_dict, frequencies):
        '''
        Convert a list of frequencies into their likeliest music note.
        
        Args:
            notes_dict  (dict) : dictionary of notes and their associated frequencies
            frequencies (list) : list of frequencies
            
        Returns:
            note         (str) : single note or None if no note identified   
        '''
        if 1.0 in frequencies.tolist():
            return 'rest' # If 1.0 is a dominant frequency assume it is background noise
        for note in notes_dict.keys():
            target = notes_dict[note]
            weight = 0
            for freq in frequencies:
                min_distance_from_target = min([abs(100*round(np.sin((np.pi/np.log(2))*np.log(freq/value)),4)) for value in target])
                if not min_distance_from_target:
                    min_distance_from_target = -100
                weight += min_distance_from_target
                
            try:
                if weight < closest_match[1]:
                    closest_match = [note, weight]
            except NameError: # On the first iteration closest_match has not yet been declared
                closest_match = [note, weight]
        return closest_match[0]
