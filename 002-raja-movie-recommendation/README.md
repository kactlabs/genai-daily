# Classic Movie Recommendation System

A daily movie recommendation system that suggests classic movies (1950-1980) available on YouTube, powered by LangChain, LangGraph, and Google Gemini.

## Features

- Daily classic movie recommendations (1950-1980)
- Genre-based categorization
- YouTube availability verification
- AI-powered movie analysis and recommendations
- Web interface for browsing recommendations

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. Get API Keys:
   - Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - YouTube Data API key from [Google Cloud Console](https://console.cloud.google.com/)

## Usage

### Run the daily recommendation system:
```bash
python main.py
```

### Run the web interface:
```bash
streamlit run app.py
```

## Project Structure

- `main.py` - Main recommendation engine
- `app.py` - Streamlit web interface
- `movie_agent.py` - LangGraph agent for movie recommendations
- `youtube_search.py` - YouTube search functionality
- `data/` - Movie database and recommendations storage
- `utils/` - Utility functions

## Example

The system will recommend classic movies like "The President's Plane Is Missing" (1973) with detailed genre analysis and YouTube availability.
