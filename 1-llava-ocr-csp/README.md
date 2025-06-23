
# Gemma OCR App

This project leverages Gemma vision capabilities and Streamlit to create a 100% locally running computer vision app that can perform both OCR and extract structured text from the image.

## Installation and setup

**Setup Ollama**:
   ```bash
   # setup ollama on linux 
   curl -fsSL https://ollama.com/install.sh | sh
   # pull gemma-3 vision model
   ollama run gemma:2b

   ollama pull llava
   ```

**Install Dependencies**:
   Ensure you have Python 3.11 or later installed.
   ```bash
   pip install streamlit ollama pillow
   ```

```
streamlit run app.py
```

---


```
https://llava-vl.github.io/
https://www.microsoft.com/en-us/research/project/llava-large-language-and-vision-assistant/
```