import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
from config import DATA_DIR, MOVIES_DB_FILE, RECOMMENDATIONS_FILE


def ensure_data_directory():
    """Ensure the data directory exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def save_recommendations(recommendations: List[Dict], date: str = None):
    """Save daily recommendations to file."""
    ensure_data_directory()
    
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    data = {
        "date": date,
        "recommendations": recommendations,
        "generated_at": datetime.now().isoformat()
    }
    
    # Load existing recommendations
    existing_data = load_all_recommendations()
    existing_data[date] = data
    
    with open(RECOMMENDATIONS_FILE, 'w') as f:
        json.dump(existing_data, f, indent=2)


def load_recommendations(date: str = None) -> List[Dict]:
    """Load recommendations for a specific date."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    all_recommendations = load_all_recommendations()
    return all_recommendations.get(date, {}).get("recommendations", [])


def load_all_recommendations() -> Dict:
    """Load all recommendations from file."""
    ensure_data_directory()
    
    if not os.path.exists(RECOMMENDATIONS_FILE):
        return {}
    
    try:
        with open(RECOMMENDATIONS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_movie_database(movies: List[Dict]):
    """Save movie database to file."""
    ensure_data_directory()
    
    data = {
        "movies": movies,
        "last_updated": datetime.now().isoformat(),
        "total_count": len(movies)
    }
    
    with open(MOVIES_DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def load_movie_database() -> List[Dict]:
    """Load movie database from file."""
    ensure_data_directory()
    
    if not os.path.exists(MOVIES_DB_FILE):
        return []
    
    try:
        with open(MOVIES_DB_FILE, 'r') as f:
            data = json.load(f)
            return data.get("movies", [])
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def format_movie_for_display(movie: Dict) -> str:
    """Format a movie recommendation for display."""
    title = movie.get('title', 'Unknown Title')
    year = movie.get('year', 'Unknown Year')
    description = movie.get('description', 'No description available.')
    genre_analysis = movie.get('genre_analysis', '')
    cast_crew = movie.get('cast_crew', '')
    
    formatted = f"🎬 **{title}** ({year})\n\n"
    formatted += f"📝 {description}\n\n"
    
    if genre_analysis:
        formatted += f"🎭 **Genre Analysis:** {genre_analysis}\n\n"
    
    if cast_crew:
        formatted += f"👥 **Cast & Crew:** {cast_crew}\n\n"
    
    # YouTube information
    if movie.get('youtube_data'):
        youtube = movie['youtube_data']
        formatted += f"📺 **YouTube:** [{youtube.get('title', 'Watch on YouTube')}]({youtube.get('url', '#')})\n"
        formatted += f"⏱️ **Duration:** {youtube.get('duration', 'Unknown')}\n"
        formatted += f"📺 **Channel:** {youtube.get('channel', 'Unknown')}\n"
        if youtube.get('views') != 'N/A':
            formatted += f"👀 **Views:** {youtube.get('views', 'Unknown')}\n"
    
    return formatted


def get_genre_for_date(date: datetime = None) -> str:
    """Get the genre for a specific date based on rotation."""
    from config import MOVIE_GENRES
    
    if date is None:
        date = datetime.now()
    
    genre_index = date.timetuple().tm_yday % len(MOVIE_GENRES)
    return MOVIE_GENRES[genre_index]


def get_stats() -> Dict:
    """Get statistics about the recommendation system."""
    all_recommendations = load_all_recommendations()
    movie_db = load_movie_database()
    
    total_days = len(all_recommendations)
    total_movies_recommended = sum(
        len(day_data.get("recommendations", [])) 
        for day_data in all_recommendations.values()
    )
    
    # Genre distribution
    genre_count = {}
    for day_data in all_recommendations.values():
        for movie in day_data.get("recommendations", []):
            # Try to extract genre from the day's data or movie data
            # This is a simplified approach
            pass
    
    return {
        "total_days": total_days,
        "total_movies_recommended": total_movies_recommended,
        "movies_in_database": len(movie_db),
        "last_recommendation_date": max(all_recommendations.keys()) if all_recommendations else None
    }


def clean_old_recommendations(days_to_keep: int = 30):
    """Clean old recommendations to save space."""
    all_recommendations = load_all_recommendations()
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    cutoff_str = cutoff_date.strftime("%Y-%m-%d")
    
    cleaned_data = {
        date: data for date, data in all_recommendations.items()
        if date >= cutoff_str
    }
    
    with open(RECOMMENDATIONS_FILE, 'w') as f:
        json.dump(cleaned_data, f, indent=2)
    
    removed_count = len(all_recommendations) - len(cleaned_data)
    return removed_count


def export_recommendations_csv(output_file: str = "recommendations_export.csv"):
    """Export all recommendations to CSV format."""
    import csv
    
    all_recommendations = load_all_recommendations()
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'date', 'title', 'year', 'description', 'genre_analysis', 
            'cast_crew', 'youtube_url', 'youtube_title', 'duration', 'channel'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for date, day_data in all_recommendations.items():
            for movie in day_data.get("recommendations", []):
                youtube_data = movie.get('youtube_data', {})
                
                row = {
                    'date': date,
                    'title': movie.get('title', ''),
                    'year': movie.get('year', ''),
                    'description': movie.get('description', ''),
                    'genre_analysis': movie.get('genre_analysis', ''),
                    'cast_crew': movie.get('cast_crew', ''),
                    'youtube_url': youtube_data.get('url', ''),
                    'youtube_title': youtube_data.get('title', ''),
                    'duration': youtube_data.get('duration', ''),
                    'channel': youtube_data.get('channel', '')
                }
                writer.writerow(row)
    
    return output_file
