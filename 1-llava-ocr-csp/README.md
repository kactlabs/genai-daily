
# Llava OCR App

This project leverages Llava vision capabilities and Streamlit to create a 100% locally running computer vision app that can perform both OCR and extract structured text from the image.

## Installation and setup

**Setup Ollama**:
   ```bash
   # setup ollama on linux 
   curl -fsSL https://ollama.com/install.sh | sh
   # pull Llava-3 vision model
   ollama run Llava:2b

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