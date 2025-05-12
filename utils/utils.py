import csv
import numpy as np
import librosa
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import matplotlib.pyplot as plt
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
import json
import utils.extract_features as extract_features


def extractFeatureToJson(file_path):
    features = extract_features.extractFeature(file_path)
    feature_dict = extract_features.aggreate_features(features)
    with open("feature_vector.json", "w") as f:
        json.dump(feature_dict, f, indent=2)

def getFeatureFromJSON(file_path):
    """
    Read features from JSON file and convert to a single feature vector.
    The JSON file should contain a dictionary of features with their values.
    """
    with open(file_path, 'r') as f:
        feature_dict = json.load(f)
    
    # Initialize an empty list to store all features
    feature_vector = []
    
    # Define the order of features to maintain consistency
    feature_order = [
        "mfcc_mean",
        "mfcc_std",
        "delta_mfcc_mean",
        "delta_mfcc_std",
        "spectral_contrast_mean",
        "spectral_centroid",
        "spectral_flatness"
    ]
    
    
    # Concatenate features in the specified order
    for feature_name in feature_order:
        if feature_name in feature_dict:
            value = feature_dict[feature_name] 
            # Handle both list and scalar values
            if isinstance(value, list):
                feature_vector.extend(value)
            else:
                feature_vector.append(value)
    
    return np.array(feature_vector)

def findCosinSimilarity(test_feature_vector, sample_feature_vector):
    """
    Calculate weighted cosine similarity between two feature vectors.
    
    Args:
        test_feature_vector: Feature vector of the test audio
        sample_feature_vector: Feature vector of the sample audio
        
    Returns:
        float: Weighted cosine similarity score between 0 and 1
    """
    # Define feature weights and their corresponding lengths
    feature_weights = {
        "mfcc_mean": 0.35,              # Main speaker fingerprint
        "mfcc_std": 0.15,               # How the voice varies
        "delta_mfcc_mean": 0.25,        # Dynamics of speech
        "delta_mfcc_std": 0.10,         # Variation in dynamics
        "spectral_contrast_mean": 0.10, # Timbre + resonance
        "spectral_centroid": 0.03,      # Pitch-like brightness
        "spectral_flatness": 0.02       # Voice quality indicator
    }
    
    # Create weight vector based on feature lengths
    feature_lengths = {
        "mfcc_mean": 11,
        "mfcc_std": 11,
        "delta_mfcc_mean": 11,
        "delta_mfcc_std": 11,
        "spectral_contrast_mean": 7,
        "spectral_centroid": 1,
        "spectral_flatness": 1
    }
    
    # Create weight vector
    weight_vector = []
    for feature, length in feature_lengths.items():
        weight = feature_weights[feature]
        weight_vector.extend([weight] * length)
    
    weight_vector = np.array(weight_vector)
    
    # Reshape vectors to 2D arrays for cosine_similarity
    test_vector = test_feature_vector.reshape(1, -1)
    sample_vector = sample_feature_vector.reshape(1, -1)
    
    # Calculate weighted cosine similarity
    # First normalize the vectors
    test_norm = test_vector / np.linalg.norm(test_vector)
    sample_norm = sample_vector / np.linalg.norm(sample_vector)

    # Apply weights to the normalized vectors
    weighted_test = test_norm * np.sqrt(weight_vector)
    weighted_sample = sample_norm * np.sqrt(weight_vector)
    # Calculate cosine similarity with weighted vectors
    similarity = cosine_similarity(weighted_test, weighted_sample)[0][0]
    return similarity


def findDTWSimilarity(
      testPath, 
      samplePath
    ):
    x = samplePath.T  # shape: (frames, 13)
    y = testPath.T
    print(x.shape)
    print(y.shape)

    window_size = y.shape[0]  # 1379
    stride = 50  # you can adjust this for speed/precision
    similarities = []

    # Flatten target y once
    y_flat = y.flatten().reshape(1, -1)
    similarity_sum = 0
    # Slide over x
    for i in tqdm(range(0, x.shape[0] - window_size + 1, stride)):
        x_window = x[i:i + window_size]  # shape: (1379, 13)
        x_flat = x_window.flatten().reshape(1, -1)

        # Compute cosine similarity
        # sim = cosine_similarity(x_flat, y_flat)[0, 0]
        distance, path = fastdtw(x_window, y, dist=euclidean)
        sim = 1 / (1 + distance)
        similarity_sum += sim
        similarities.append(sim)

    print(similarity_sum)
    # Plotting
    plt.figure(figsize=(12, 5))
    plt.plot(similarities)
    plt.title('DƯT Similarity between sliding x and y')
    plt.xlabel('Window Start Frame Index')
    plt.ylabel('DƯT Similarity')
    plt.grid(True)
    plt.tight_layout()
    plt.show()