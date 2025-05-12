import worker as worker
import utils.extract_features as extract_features
import utils.utils as utils
import numpy as np
test_file = "CNDPT-20250509T093006Z-1-001\CNDPT\Learning a new language\Learning a new language-01.wav"
test_file_2 = "CNDPT-20250509T093006Z-1-001\CNDPT\Learning a new language\Learning a new language-04.wav"
test_file_3 = "CNDPT-20250509T093006Z-1-001\CNDPT\How to speak\How to speak-03.wav"


def init_new_data_source(directory):
    """
    Raw feature extraction placed inside the same directory,
    the normalized feature for comparison is stored in the normalized_features.json file
    """
    agent = worker.Worker(directory)
    agent.process_directory(directory)
    agent.normalize_features()


# Example usage
if __name__ == "__main__":
    cndpt_directory = "CNDPT-20250509T093006Z-1-001/CNDPT"
    agent = worker.Worker(cndpt_directory)

    print(agent.find_similar_files(test_file_3, 5))

    



