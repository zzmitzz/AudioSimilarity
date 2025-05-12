from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import worker as worker

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize worker agent
cndpt_directory = "CNDPT-20250509T093006Z-1-001/CNDPT"
agent = worker.Worker(cndpt_directory)

@app.route('/api/find-similar', methods=['POST'])
def find_similar_files():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Find similar files
            similar_files = agent.find_similar_files(filepath, 5)
            
            # Normalize file paths to use forward slashes
            normalized_similar_files = [
                [path.replace('\\', '/'), similarity]
                for path, similarity in similar_files
            ]
            
            # Clean up the uploaded file
            os.remove(filepath)
            
            return jsonify({
                'similar_files': normalized_similar_files
            })
        except Exception as e:
            # Clean up the uploaded file in case of error
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': str(e)}), 500

@app.route('/api/audio', methods=['POST'])
def get_audio():
    try:
        if not request.json or 'filename' not in request.json:
            return jsonify({'error': 'No filename provided in request body'}), 400
            
        file_path = request.json['filename']
        
        # Check if file exists and is within allowed directory
        if not os.path.exists(file_path) or not os.path.abspath(file_path).startswith(os.path.abspath(cndpt_directory)):
            return jsonify({'error': 'File not found'}), 404
            
        return send_file(file_path, mimetype='audio/wav')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 