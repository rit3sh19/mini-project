🎧 Profanity Detection & Censorship System
  A Streamlit-based application that detects profanity from audio using Whisper transcription and classifies the text using a toxicity detection model (BERT-based). The project also uses PyDub to process audio segments, censor bad words, and generate safe outputs.
🚀 Features
  Upload audio files for profanity detection
  Whisper-based speech-to-text transcription
  Toxic-BERT (or similar) model for profanity classification
  Word-level profanity detection
  Censoring & audio modification using PyDub
Streamlit UI for easy usage
  📦 Installation & Setup
    1️⃣ Clone the Repository
        git clone https://github.com/your-username/profanity-detection-system.git
        cd profanity-detection-system
    2️⃣ Create a Virtual Environment
        python -m venv venv
        source venv/bin/activate   # Mac/Linux
        venv\Scripts\activate      # Windows
    3️⃣ Install Requirements
        Make sure FFmpeg is installed (required for Whisper & PyDub).
        Install Python dependencies:
        pip install -r requirements.txt
        Install FFmpeg:
          Windows:
            Download from https://www.gyan.dev/ffmpeg
          Linux (Ubuntu):
            sudo apt install ffmpeg
          Mac:
            brew install ffmpeg
    ▶️ Running the Project
          Start the Streamlit App
          streamlit run app.py
          The app will open at:
          http://localhost:8501
          📁 Project Structure
          📦 profanity-detection-system
           ┣ 📜 app.py
           ┣ 📜 censor.py
           ┣ 📜 model.py
           ┣ 📜 utils.py
           ┣ 📜 requirements.txt
           ┗ 📁 assets / samples / (optional)
    🧠 How It Works
            User uploads an audio file
            Whisper transcribes speech → text
            Toxic-BERT classifies text for profanity
            PyDub locates timestamps → censors audio
            Output is displayed + downloadable
    ⚙️ Requirements
        Python 3.10+
        FFmpeg
        Internet (if using Whisper API or HuggingFace pipeline)
        Streamlit
        📝 Notes
          Make sure your microphone permissions are enabled if you add live recording
          Whisper may take time depending on CPU/GPU
          Toxic-BERT model can be swapped with any text classifier
