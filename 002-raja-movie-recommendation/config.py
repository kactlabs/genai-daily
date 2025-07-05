import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Movie Configuration
CLASSIC_MOVIE_YEARS = (1950, 1980)
MOVIE_GENRES = [
    "Drama", "Thriller", "Action", "Comedy", "Horror", "Science Fiction",
    "Western", "Romance", "Mystery", "Adventure", "War", "Crime",
    "Musical", "Fantasy", "Film Noir", "Documentary"
]

# YouTube Search Configuration
MAX_SEARCH_RESULTS = 10
SEARCH_QUERY_TEMPLATE = "{title} {year} full movie"

# Database Configuration
DATA_DIR = "data"
MOVIES_DB_FILE = f"{DATA_DIR}/movies.json"
RECOMMENDATIONS_FILE = f"{DATA_DIR}/daily_recommendations.json"

# LangChain Configuration
MODEL_NAME = "gemini-pro"
TEMPERATURE = 0.7
MAX_TOKENS = 1000

# Recommendation Configuration
DAILY_RECOMMENDATION_COUNT = 3
GENRE_ROTATION_DAYS = 7
