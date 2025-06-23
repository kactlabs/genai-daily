
# Llava OCR App

A powerful local OCR application built with Llava vision model and Streamlit. Extract and structure text from images with advanced computer vision capabilities, running entirely on your machine without external API dependencies.

## Installation and setup

**Setup Ollama**:
   ```bash
   # setup ollama on linux 
   curl -fsSL https://ollama.com/install.sh | sh

   # pull Llava-3 vision model
   ollama pull llava
   ```

**Install Dependencies**:
   Ensure you have Python 3.11 or later installed.
   ```bash
   pip install -r requirements.txt
   ```

**Run**:
```
streamlit run app.py
```


**Sources**:
```
https://llava-vl.github.io/
https://www.microsoft.com/en-us/research/project/llava-large-language-and-vision-assistant/
```
