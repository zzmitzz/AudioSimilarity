import librosa
import librosa.display
import matplotlib.pyplot as plt
import soundfile as sf
import numpy as np
import pandas as pd



def extract_MFCCs(
    data,
    sr = 16000,
    nu_filter = 13,
    n_fft = 2048,
    hop_length = 160
    ):
  mfccs = librosa.feature.mfcc(y=data, sr=sr, n_mfcc=nu_filter, n_fft=n_fft, hop_length=hop_length)
  # Remove first two coefficients (0 and 1) as they are dominant
  mfccs = mfccs[2:]
  delta_mfccs = librosa.feature.delta(mfccs)
  return mfccs, delta_mfccs

def extract_spectral_contrast(
    data,
    sr = 16000,
    n_bands = 6
    ):
  spectral_contrast = librosa.feature.spectral_contrast(y=data, sr=sr, n_bands=n_bands)
  return spectral_contrast

def extract_spectral_centroid(
    data,
    sr = 16000,
    n_fft = 2048,
    hop_length = 160
    ):
  spectral_centroid = librosa.feature.spectral_centroid(y=data, sr=sr, n_fft=n_fft, hop_length=hop_length)
  return spectral_centroid

def extract_spectral_flatness(
    data
    ):
  spectral_flatness = librosa.feature.spectral_flatness(y=data)
  return spectral_flatness


def extractFeature(
    audio_file, 
    mfcc_filter = 13, 
    spectral_contrast_bands = 6,
    n_fft = 2048,
    hop_length = 160,
    sr = 16000
    ):
  
  features = {}
  y, sr = librosa.load(audio_file, sr=None)
  
  mfcc, delta_mfcc = extract_MFCCs(y, sr, mfcc_filter, n_fft, hop_length)
  

  features['mfcc'] = mfcc

  features['delta_mfcc'] = delta_mfcc
  
  spectral_contrast = extract_spectral_contrast(y, sr, spectral_contrast_bands)
  features['spectral_contrast'] = spectral_contrast
  
  spectral_centroid = extract_spectral_centroid(y, sr, n_fft, hop_length)
  features['spectral_centroid'] = spectral_centroid
  
  spectral_flatness = extract_spectral_flatness(y)
  features['spectral_flatness'] = spectral_flatness
  
  return features

def aggreate_features(features):
  mfcc_mean = np.mean(features['mfcc'], axis=1)
  mfcc_std = np.std(features['mfcc'], axis=1)

  delta_mfcc_mean = np.mean(features['delta_mfcc'], axis=1)
  delta_mfcc_std = np.std(features['delta_mfcc'], axis=1)

  spectral_contrast_mean = np.mean(features['spectral_contrast'], axis=1)
  spectral_centroid = np.mean(features['spectral_centroid'])
  spectral_flatness = np.mean(features['spectral_flatness'], axis=1)
  
  # Create a dictionary with feature names and their values
  feature_dict = {
    "mfcc_mean": mfcc_mean.tolist(),
    "mfcc_std": mfcc_std.tolist(),
    "delta_mfcc_mean": delta_mfcc_mean.tolist(),
    "delta_mfcc_std": delta_mfcc_std.tolist(),
    "spectral_contrast_mean": spectral_contrast_mean.tolist(),
    "spectral_centroid": float(spectral_centroid),  # Convert scalar to float
    "spectral_flatness": spectral_flatness.tolist()
  }
  
  return feature_dict
