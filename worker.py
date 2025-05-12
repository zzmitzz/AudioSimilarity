import utils.observe_init_data as observe_init_data
import utils.pre_processing as pre_processing
import numpy as np
import utils.extract_features as extract_features
import utils.utils as utils
import json
import os
from tqdm import tqdm


class Worker:
    def __init__(self, directory_path):
        self.directory_path = directory_path

    def process_directory(self, directory_path):
        """
        Process all WAV files in the given directory and its subdirectories.
        For each WAV file, extract features and save them as a JSON file with the same name.
        """
    # First, collect all WAV files
        wav_files = []
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.lower().endswith('.wav'):
                    wav_files.append(os.path.join(root, file))
        
        # Process files with progress bar
        for wav_path in tqdm(wav_files, desc="Processing WAV files", unit="file"):
            # Create the corresponding JSON file path
            json_path = os.path.splitext(wav_path)[0] + '.json'
            
            try:
                # Extract features
                features = extract_features.extractFeature(wav_path)
                feature_dict = extract_features.aggreate_features(features)
                
                # Save to JSON
                with open(json_path, 'w') as f:
                    json.dump(feature_dict, f, indent=4)
                
                tqdm.write(f"✓ Processed: {os.path.basename(wav_path)}")
            except Exception as e:
                tqdm.write(f"✗ Error processing {os.path.basename(wav_path)}: {str(e)}")

    def normalize_features(self):
        """
        Normalize feature vectors across all JSON files in the directory.
        Each feature type is normalized separately using min-max normalization.
        Saves normalized features to a new 'normalized_features' directory.
        Also saves feature statistics (min/max) to configs.json for future normalization.
        """
        # Create normalized features directory
        normalized_dir = os.path.join(self.directory_path, 'normalized_features')
        os.makedirs(normalized_dir, exist_ok=True)

        # Collect all JSON files
        json_files = []
        for root, dirs, files in os.walk(self.directory_path):
            for file in files:
                if file.lower().endswith('.json'):
                    json_files.append(os.path.join(root, file))

        if not json_files:
            print("No JSON files found for normalization")
            return

        # First pass: collect all feature values for each feature type
        feature_values = {}
        for json_path in tqdm(json_files, desc="Collecting features", unit="file"):
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)
                    for feature_name, value in data.items():
                        if feature_name not in feature_values:
                            feature_values[feature_name] = []
                        # Handle both scalar and list values, filter out non-numeric
                        if isinstance(value, list):
                            for v in value:
                                if isinstance(v, (int, float)):
                                    feature_values[feature_name].append(v)
                                else:
                                    tqdm.write(f"Warning: Non-numeric value in list for feature '{feature_name}' in {os.path.basename(json_path)}: {v}")
                        elif isinstance(value, (int, float)):
                            feature_values[feature_name].append(value)
                        else:
                            tqdm.write(f"Warning: Non-numeric value for feature '{feature_name}' in {os.path.basename(json_path)}: {value}")
            except Exception as e:
                tqdm.write(f"\u2717 Error reading {os.path.basename(json_path)}: {str(e)}")

        # Calculate min and max for each feature type
        feature_stats = {}
        for feature_name, values in feature_values.items():
            if values:
                feature_stats[feature_name] = {
                    'min': min(values),
                    'max': max(values)
                }
            else:
                tqdm.write(f"Warning: No numeric values found for feature '{feature_name}'. Setting min/max to 0.")
                feature_stats[feature_name] = {'min': 0, 'max': 0}

        # Save feature statistics to configs.json
        configs_path = os.path.join(normalized_dir, 'configs.json')
        with open(configs_path, 'w') as f:
            json.dump(feature_stats, f, indent=4)
        tqdm.write(f"\u2713 Saved feature statistics to {configs_path}")

        # Second pass: normalize and save to new directory
        for json_path in tqdm(json_files, desc="Normalizing features", unit="file"):
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)

                # Normalize each feature
                normalized_data = {}
                for feature_name, value in data.items():
                    stats = feature_stats[feature_name]
                    if stats['max'] != stats['min']:  # Avoid division by zero
                        if isinstance(value, list):
                            normalized_value = [(v - stats['min']) / (stats['max'] - stats['min']) if isinstance(v, (int, float)) else 0.5 for v in value]
                        elif isinstance(value, (int, float)):
                            normalized_value = (value - stats['min']) / (stats['max'] - stats['min'])
                        else:
                            normalized_value = 0.5
                    else:
                        normalized_value = 0.5 if isinstance(value, list) else 0.5
                    normalized_data[feature_name] = normalized_value

                # Create relative path structure in normalized directory
                rel_path = os.path.relpath(json_path, self.directory_path)
                normalized_path = os.path.join(normalized_dir, rel_path)
                
                # Create subdirectories if they don't exist
                os.makedirs(os.path.dirname(normalized_path), exist_ok=True)

                # Save normalized data
                with open(normalized_path, 'w') as f:
                    json.dump(normalized_data, f, indent=4)

                tqdm.write(f"\u2713 Normalized: {os.path.basename(json_path)}")
            except Exception as e:
                tqdm.write(f"\u2717 Error normalizing {os.path.basename(json_path)}: {str(e)}")

    
    def get_normalized_test_feature(self, test_file_path):
        """
        Extract, aggregate and normalize features from a test audio file using saved normalization coefficients.
        
        Args:
            test_file_path (str): Path to the test WAV file
            
        Returns:
            dict: Dictionary containing normalized feature values
        """
        # Extract and aggregate features
        features = extract_features.extractFeature(test_file_path)
        feature_dict = extract_features.aggreate_features(features)
        
        # Load normalization coefficients from configs.json
        configs_path = os.path.join(self.directory_path, 'normalized_features', 'configs.json')
        try:
            with open(configs_path, 'r') as f:
                feature_stats = json.load(f)
        except Exception as e:
            raise Exception(f"Error loading normalization coefficients: {str(e)}")
        
        # Normalize features using saved coefficients
        normalized_data = {}
        for feature_name, value in feature_dict.items():
            if feature_name not in feature_stats:
                raise Exception(f"Feature {feature_name} not found in normalization coefficients")
                
            stats = feature_stats[feature_name]
            if stats['max'] != stats['min']:  # Avoid division by zero
                if isinstance(value, list):
                    # Normalize each element in the list
                    normalized_value = [(v - stats['min']) / (stats['max'] - stats['min']) for v in value]
                else:
                    normalized_value = (value - stats['min']) / (stats['max'] - stats['min'])
            else:
                normalized_value = 0.5 if isinstance(value, list) else 0.5
            normalized_data[feature_name] = normalized_value
            
        return normalized_data

    def convert_dict_to_array(self, dict):
        all_values = []
        for key, value in dict.items():
            if isinstance(value, list):
                all_values.extend(value)
            else:
                all_values.append(value)
        # Convert to numpy array
        test = np.array(all_values)
        return test
    
    def find_similar_files(self, input_file_path, top_n=5):
        """
        Find the top N most similar files to the input file based on feature similarity.
        
        Args:
            input_file_path (str): Path to the input WAV file
            top_n (int): Number of similar files to return
            
        Returns:
            list: List of tuples (file_path, similarity_score) for the top N most similar files
        """
        # Get normalized features for the input file
        input_features = self.get_normalized_test_feature(input_file_path)
        input_vector = self.convert_dict_to_array(input_features)
        
        # Directory containing normalized features
        normalized_dir = os.path.join(self.directory_path, 'normalized_features')
        
        # Store similarity scores
        similarity_scores = []
        
        # Collect all JSON files first
        json_files = []
        for root, dirs, files in os.walk(normalized_dir):
            for file in files:
                if file.lower().endswith('.json') and file != 'configs.json':
                    json_files.append(os.path.join(root, file))
        
        # Read and compare with all normalized feature files with progress bar
        for file_path in tqdm(json_files, desc="Comparing files", unit="file"):
            try:
                compare_vector = utils.getFeatureFromJSON(file_path)
                
                similarity = utils.findCosinSimilarity(input_vector, compare_vector)
                
                # # Store original WAV file path (remove .json extension and normalized_features part)
                original_path = os.path.relpath(file_path, normalized_dir)
                original_path = os.path.splitext(original_path)[0] + '.wav'
                original_path = os.path.join(self.directory_path, original_path)
                print(compare_vector.shape," : ", original_path)
                similarity_scores.append((original_path, similarity))
                
            except Exception as e:
                tqdm.write(f"Error processing {os.path.basename(file_path)}: {str(e)}")
        
        # Sort by similarity score in descending order and get top N
        similarity_scores.sort(key=lambda x: x[1], reverse=True)
        return similarity_scores[:top_n]
