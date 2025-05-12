import librosa
import librosa.display
import matplotlib.pyplot as plt
import soundfile as sf
import numpy as np


def time_domain_chart(audio_file):  # Modified to accept an axes object
    fig,ax = plt.subplots(1,1,figsize=(10,4))
    y, sr = librosa.load(audio_file)
    # Normalize the signal to have maximum amplitude of 1
    y_normalized = y / np.max(np.abs(y))
    # Convert to dB scale and invert it so quiet parts are negative
    y_section_db = -librosa.amplitude_to_db(np.abs(y_normalized), ref=1.0)
    librosa.display.waveshow(y_section_db, sr=sr, ax=ax)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude (dB)")
    ax.set_title("Time Domain Representation of Audio (dB Scale)")
    plt.show()

def frequency_domain_chart(audio_file):
    n_fft = 1024 # 1024 samples per frame suitable for human hearing
    fig,ax = plt.subplots(1,1,figsize=(12,16))
    y, sr = librosa.load(audio_file)

    D = librosa.stft(y, n_fft=n_fft)
    # Get the magnitude spectrum
    magnitude_spectrum = np.abs(D)
    magnitude_spectrum_db = librosa.amplitude_to_db(magnitude_spectrum)
    print(magnitude_spectrum_db)
    print(magnitude_spectrum_db.shape)

    # Average the spectrum across time to get a frequency distribution
    frequency_distribution_db = np.mean(magnitude_spectrum, axis=1)
    frequencies = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    ax.plot(frequencies[:len(frequency_distribution_db)], frequency_distribution_db)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude")
    ax.set_title(f"Frequency Chart of {audio_file}")

    plt.tight_layout()
    plt.show()