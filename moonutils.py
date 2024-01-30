from pydub import AudioSegment, effects
from scipy.fft import rfft, rfftfreq

import numpy as np
def calculate_loudness(chunk):
    # Normalize the chunk for consistent loudness
    normalized_chunk = effects.normalize(chunk)
    # Calculate loudness
    loudness = normalized_chunk.dBFS
    return loudness

import simpleaudio as sa
def calculate_average_frequency(chunk):
    # Get raw audio data as numpy array
    samples = np.array(chunk.get_array_of_samples())
    # Perform Fourier Transform
    yf = rfft(samples)
    xf = rfftfreq(len(samples), 1 / chunk.frame_rate)
    # Calculate average frequency
    avg_freq = np.sum(xf * np.abs(yf)) / np.sum(np.abs(yf))
    return avg_freq

def load_and_slice_audio(file_path, num_chunks, soundrange):
    song = AudioSegment.from_mp3(file_path)
    first_10_seconds = song[soundrange[0]:soundrange[1]]  # Get the first 10 seconds
    chunk_length = len(first_10_seconds) // num_chunks
    chunks = [first_10_seconds[i * chunk_length:(i + 1) * chunk_length] for i in range(num_chunks)]
    return chunks

def play_chunk(chunk):
    playback = sa.play_buffer(
        chunk.raw_data,
        num_channels=chunk.channels,
        bytes_per_sample=chunk.sample_width,
        sample_rate=chunk.frame_rate
    )
    #playback.wait_done()
    avg_freq = calculate_average_frequency(chunk)
    loudness = calculate_loudness(chunk)
    print(f"Average frequency: {avg_freq:.2f} Hz")
    print(f"Loudness: {loudness:.2f} dBFS")
    #if either is nan or inf then set to 0
    if np.isnan(avg_freq) or np.isinf(avg_freq):
        avg_freq = 0
    if np.isnan(loudness) or np.isinf(loudness):
        loudness = 0

    return avg_freq, loudness