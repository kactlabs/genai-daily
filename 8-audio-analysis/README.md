# 🎵 Audio Analysis Toolkit

A modern, streamlined audio analysis application powered by AssemblyAI and Streamlit. Upload audio files to get AI-powered transcription, speaker detection, sentiment analysis, topic extraction, and interactive Q&A capabilities.

## ✨ Features

- **📝 Transcription** - High-quality speech-to-text with precise timestamps
- **👥 Speaker Detection** - Automatically identify and separate different speakers
- **😊 Sentiment Analysis** - Analyze emotional tone and context throughout the audio
- **📋 Summarization** - Get AI-generated summaries of key points and insights
- **🏷️ Topic Detection** - Discover main themes and subjects discussed
- **💬 Interactive Q&A** - Ask questions about your audio content using AI

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- AssemblyAI API key ([Get one free here](https://www.assemblyai.com/))

### Installation

1. **Clone or download the project**
   ```bash
   cd 8-audio-analysis
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit assemblyai python-dotenv
   ```

3. **Set up your API key**
   
   Create a `.env` file in the project directory:
   ```
   ASSEMBLYAI_API_KEY=your_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser** to `http://localhost:8501`

## 🎯 Usage

1. **Upload Audio**: Use the sidebar to upload your audio file (MP3, WAV, M4A, MP4, FLAC)
2. **Wait for Processing**: The AI will analyze your audio (this may take a few minutes)
3. **Explore Results**: Use the tabs to view transcription, summary, speakers, sentiment, topics
4. **Ask Questions**: Use the Chat tab to ask questions about your audio content

## 🧪 Testing

Test your setup with the included test script:

```bash
python test.py
```

This will verify your API key and test basic transcription functionality.

## 📁 Supported Formats

- **MP3** - Most common audio format
- **WAV** - Uncompressed audio
- **M4A** - Apple audio format
- **MP4** - Video files with audio
- **FLAC** - Lossless audio compression

## 🎨 Customization

The application uses a clean, modern design with:
- Light theme optimized for readability
- Responsive layout that works on desktop and mobile
- Smooth animations and transitions
- Custom CSS styling in `styles.css`

## 🔧 Configuration

The app automatically loads configuration from your `.env` file:

```env
ASSEMBLYAI_API_KEY=your_api_key_here
```

## 📊 Features in Detail

### Transcription
- Word-level timestamps
- High accuracy speech recognition
- Support for multiple languages
- Automatic punctuation and formatting

### Speaker Detection
- Automatic speaker identification
- Speaker-separated dialogue
- Utterance counting and analysis
- Speaker timeline visualization

### Sentiment Analysis
- Positive, negative, and neutral sentiment detection
- Timestamp-based sentiment tracking
- Emotional tone analysis throughout the audio
- Visual sentiment timeline

### Topic Detection
- AI-powered topic extraction
- Confidence scores for each topic
- Industry-standard topic categories
- Visual topic distribution

### Interactive Q&A
- Ask natural language questions about your audio
- AI-powered responses based on transcript content
- Conversational interface
- Context-aware answers

## 🛠️ Technical Details

- **Frontend**: Streamlit with custom CSS
- **AI Engine**: AssemblyAI API
- **Language**: Python 3.8+
- **Dependencies**: Minimal and lightweight
- **Architecture**: Clean, modular code structure

## 📝 Code Structure

```
8-audio-analysis/
├── app.py          # Main Streamlit application
├── test.py         # Test script for API functionality
├── styles.css      # Custom CSS styling
├── .env           # Environment variables (API key)
└── README.md      # This documentation
```

## 🤝 Contributing

This is a clean, rewritten version of the audio analysis toolkit. The code is:
- Well-documented with clear function names
- Modular and easy to extend
- Following Python best practices
- Optimized for performance and user experience

## 📄 License

This project is open source and available under standard terms.

## 🆘 Support

If you encounter issues:
1. Check that your API key is correctly set in the `.env` file
2. Ensure your audio file is in a supported format
3. Run the test script to verify your setup
4. Check the Streamlit logs for detailed error messages

---

**Built with ❤️ using AssemblyAI and Streamlit**
