import librosa
import librosa.display
import matplotlib.pyplot as plt
import soundfile as sf
import numpy as np
import utils.extract_features as extract_features
import utils.pre_processing as pre_processing


test_file = "CNDPT-20250509T093006Z-1-001/CNDPT/Buy happiness/Buy happiness-01.wav"

# extractSpectralContrastFeats("CNDPT-20250509T093006Z-1-001/CNDPT/Buy happiness/Buy happiness-01.wav")

# amplitude_array = pre_processing.re_sampling(
#     test_file)

# amplitude_array = pre_processing.normalize_amplitude(
#     test_file, saved_new_sample=True)

# print(amplitude_array)

