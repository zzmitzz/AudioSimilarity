import librosa
import soundfile as sf
import numpy as np

def re_sampling(audio_file, target_sr = 16000, saved_new_sample = False):
    """
    16000Hz is good choice for voice audio processing
    """
    y, sr = librosa.load(audio_file)
    y_resampled = librosa.resample(y, orig_sr=sr, target_sr=target_sr)
    if saved_new_sample:
        sf.write('output_16k.wav', y_resampled, 16000)
    print("Output sample rate: ", y_resampled)
    return y_resampled

def normalize_amplitude(input_data, saved_new_sample = False):
    """
    normalize the amplitude of the audio file, 
    divide all the amplitude by the max amplitude of the audio file
    """
    # Load the audio file if input_data is a file path
    if isinstance(input_data, str):
        y, sr = librosa.load(input_data)
    else:
        y = input_data  
        sr = None

    # Manual normalization
    max_amplitude = np.max(np.abs(y))
    y_normalized = y / max_amplitude
    np.savetxt('raw_amplitude_data.txt', y_normalized)
    print("Normalized amplitude: ", y_normalized)
    if saved_new_sample and sr is not None:
        sf.write('output_normalized.wav', y_normalized, sr)
    
    return y_normalized

def remove_silence(input_data, threshold=0.009, min_silence_duration=0.1, sr=16000, saved_new_sample=False):
    """
    Remove silence segments from audio signal where amplitude is below threshold.
    
    Args:
        input_data: Audio signal array or file path
        threshold: Amplitude threshold for silence detection (default: 0.09)
        min_silence_duration: Minimum duration of silence in seconds (default: 0.1)
        sr: Sample rate of the audio (default: 16000)
        saved_new_sample: Whether to save the processed audio (default: False)
    
    Returns:
        processed_audio: Audio signal with silence segments removed
    """
    # Load the audio file if input_data is a file path
    if isinstance(input_data, str):
        y, sr = librosa.load(input_data)
    else:
        y = input_data

    # Find where amplitude is below threshold
    is_silence = np.abs(y) < threshold
    
    # Find the start and end indices of silence segments
    silence_starts = np.where(np.diff(is_silence.astype(int)) == 1)[0]
    silence_ends = np.where(np.diff(is_silence.astype(int)) == -1)[0]
    
    # Handle edge cases
    if len(silence_starts) > 0 and len(silence_ends) > 0:
        if silence_starts[0] > silence_ends[0]:
            silence_ends = silence_ends[1:]
        if len(silence_starts) > len(silence_ends):
            silence_starts = silence_starts[:-1]
    
    # Create a mask for non-silence segments
    mask = np.ones(len(y), dtype=bool)
    
    # Mark silence segments in the mask
    for start, end in zip(silence_starts, silence_ends):
        duration = (end - start) / sr
        if duration >= min_silence_duration:
            mask[start:end] = False
    
    # Apply the mask to remove silence
    processed_audio = y[mask]
    
    if saved_new_sample:
        sf.write('output_no_silence.wav', processed_audio, sr)
    
    print(f"Removed silence segments. Original length: {len(y)}s, New length: {len(processed_audio)}s")
    return processed_audio

def preprocess_voice(input_data, sr=16000, saved_new_sample=False):
    """
    Complete voice preprocessing pipeline:
    1. Resampling
    2. Noise reduction
    3. Voice enhancement
    4. Amplitude normalization
    5. Silence removal
    """

    # Apply preprocessing steps
    y = re_sampling(input_data, target_sr=sr)
    y = normalize_amplitude(y)
    y = remove_silence(y, threshold=0.009, min_silence_duration=0.1, sr=sr)
    
    if saved_new_sample:
        sf.write('output_processed_voice.wav', y, sr)
    
    return y