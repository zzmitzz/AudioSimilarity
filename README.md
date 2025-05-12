# Audio Similarity Project

## Requirements
- Python 3.11.0rc2 or higher

## Setup Instructions

1. **Dataset Preparation**
   - Place the audio dataset in the following directory:
   ```
   CNDPT-20250509T093006Z-1-001/CNDPT
   ```

2. **Environment Setup**
   ```bash
   # Create a virtual environment
   python -m venv venv

   # Activate the virtual environment
   # For Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # For Windows Command Prompt:
   .\venv\Scripts\activate.bat
   # For Unix/MacOS:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```

5. **Run the Front End**
   ```bash
   cd react_fe
   npm ci
   npm run dev
   ```

## Project Structure
```
.
├── CNDPT-20250509T093006Z-1-001/
│   └── CNDPT/           # Audio dataset directory
├── venv/                # Virtual environment
├── app.py              # Main application file
├── requirements.txt    # Project dependencies
└── README.md          # This file
```

## License
zzmitzz[@github]
## Contributing
Holy thanks to Cursor