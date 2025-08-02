🎙️ EchoVerse: AI-Powered Audiobook Creation App
EchoVerse is a Streamlit application that transforms text into expressive, AI-narrated audiobooks. It leverages a powerful Large Language Model (LLM) to rewrite your text in a tone of your choice and a Text-to-Speech (TTS) service to generate a downloadable MP3 file.

Features:

Multi-Source Text Input: Input your text via a file upload, a text area, or directly from your microphone via a voice-to-text feature.

AI Text Rewriting: Choose from three distinct tones (Neutral, Suspenseful, or Inspiring) to have the text rewritten by an IBM Granite model.

Audio Generation: Convert the rewritten text into an audio file.

Preview & Download: Listen to the generated audio directly in the app and download it as an MP3 file.

Intuitive UI: A clean and easy-to-use interface built with Streamlit.

🚀 Getting Started
Follow these steps to get EchoVerse up and running on your local machine.

1. Prerequisites
Python 3.10 or higher

Anaconda or another Python virtual environment manager

Hugging Face Access Token: You will need a read-access token to download the IBM Granite model. You can get one from your Hugging Face settings.

2. Clone the Repository
Open your terminal or command prompt and run the following command to clone the project to your local machine:

Bash

git clone https://github.com/vizm3/EchoVerse-App.git
cd EchoVerse-App
3. Set Up the Environment
It's highly recommended to use a virtual environment to manage dependencies.

Bash

# Create and activate a new Conda environment
conda create -n echoverse_env python=3.10 -y
conda activate echoverse_env

# Install the required libraries from requirements.txt
pip install -r requirements.txt
4. Set Your Credentials
You must set your Hugging Face Access Token as an environment variable for the application to be able to download and use the model.

Windows (Command Prompt):

Bash

set HUGGING_FACE_HUB_TOKEN="your_token_here"
macOS / Linux (Terminal):

Bash

export HUGGING_FACE_HUB_TOKEN="your_token_here"
5. Run the Application
With your environment active and credentials set, you can now launch the application.

Bash

streamlit run app.py
This command will start a local web server and open the EchoVerse application in your default web browser at http://localhost:8501.

🗂️ Project Structure
The project is organized into the following files:

app.py: The main Streamlit application script that handles the UI and orchestrates the workflow.

llm_handler.py: Contains the logic for loading the IBM Granite model and rewriting the text based on the selected tone.

tts_handler.py: Manages the text-to-speech conversion using the gTTS library.

requirements.txt: A list of all necessary Python libraries for the project.

🤝 Contributing
We welcome contributions! If you would like to contribute, please feel free to fork the repository and submit a pull request.