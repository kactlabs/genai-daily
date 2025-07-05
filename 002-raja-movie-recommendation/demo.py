#!/usr/bin/env python3
"""
Demo script for the Classic Movie Recommendation System
Shows how the system works with sample data (no API keys required)
"""

import json
import random
from datetime import datetime
from utils import get_genre_for_date, format_movie_for_display
from config import MOVIE_GENRES


def load_sample_movies():
    """Load sample movies from the data file."""
    try:
        with open('data/sample_movies.json', 'r') as f:
            data = json.load(f)
            return data['classic_movies_1950_1980']
    except FileNotFoundError:
        print("❌ Sample movies file not found. Please ensure data/sample_movies.json exists.")
        return []


def simulate_youtube_search(movie):
    """Simulate YouTube search results for demo purposes."""
    # Simulate that some movies are found on YouTube
    if movie.get('likely_youtube_available', False):
        return {
            'title': f"{movie['title']} ({movie['year']}) - Full Movie",
            'url': f"https://youtube.com/watch?v=demo_{movie['title'].replace(' ', '_').lower()}",
            'thumbnail': 'https://via.placeholder.com/320x180?text=Movie+Thumbnail',
            'duration': f"{random.randint(80, 150)}:{random.randint(10, 59):02d}",
            'channel': random.choice(['Classic Movies', 'Vintage Cinema', 'Old Hollywood', 'Film Archive']),
            'views': f"{random.randint(10, 500)}K views",
            'published': f"{random.randint(1, 10)} years ago"
        }
    return None


def demo_daily_recommendations():
    """Demo daily movie recommendations."""
    print("🎬 Classic Movie Recommendation System - DEMO")
    print("=" * 60)
    
    # Get today's genre
    today_genre = get_genre_for_date()
    print(f"🎭 Today's Genre: {today_genre}")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    print()
    
    # Load sample movies
    sample_movies = load_sample_movies()
    if not sample_movies:
        return
    
    # Filter movies by today's genre (or similar genres)
    genre_movies = [movie for movie in sample_movies if movie['genre'] == today_genre]
    
    # If no exact matches, get movies from similar genres
    if not genre_movies:
        if today_genre in ['Thriller', 'Mystery', 'Crime']:
            genre_movies = [movie for movie in sample_movies if movie['genre'] in ['Thriller', 'Mystery', 'Crime']]
        elif today_genre == 'Horror':
            genre_movies = [movie for movie in sample_movies if movie['genre'] == 'Horror']
        elif today_genre in ['Comedy', 'Musical']:
            genre_movies = [movie for movie in sample_movies if movie['genre'] in ['Comedy', 'Musical']]
        else:
            # Fallback to any movies
            genre_movies = sample_movies[:3]
    
    # Select up to 3 movies
    selected_movies = random.sample(genre_movies, min(3, len(genre_movies)))
    
    print(f"🎯 Found {len(selected_movies)} {today_genre} recommendations:")
    print("=" * 60)
    
    for i, movie in enumerate(selected_movies, 1):
        print(f"\n{i}. 🎬 {movie['title']} ({movie['year']})")
        print("-" * 50)
        print(f"📝 {movie['description']}")
        print(f"🎭 Genre: {movie['genre']}")
        print(f"👥 Cast & Crew: {movie['cast_crew']}")
        print(f"🎬 Director: {movie['director']}")
        
        # Simulate YouTube search
        youtube_data = simulate_youtube_search(movie)
        if youtube_data:
            print(f"\n📺 Available on YouTube:")
            print(f"   Title: {youtube_data['title']}")
            print(f"   🔗 URL: {youtube_data['url']}")
            print(f"   ⏱️ Duration: {youtube_data['duration']}")
            print(f"   📺 Channel: {youtube_data['channel']}")
            print(f"   👀 Views: {youtube_data['views']}")
            print(f"   📅 Published: {youtube_data['published']}")
        else:
            print(f"\n❌ Not currently available on YouTube")
        
        print()


def demo_genre_recommendations():
    """Demo genre-specific recommendations."""
    print("\n🎭 Genre-Specific Recommendations Demo")
    print("=" * 60)
    
    sample_movies = load_sample_movies()
    if not sample_movies:
        return
    
    # Show available genres in sample data
    available_genres = list(set(movie['genre'] for movie in sample_movies))
    print(f"📚 Available genres in sample data: {', '.join(available_genres)}")
    
    # Demo with Horror genre
    demo_genre = "Horror"
    horror_movies = [movie for movie in sample_movies if movie['genre'] == demo_genre]
    
    print(f"\n🎯 {demo_genre} Movies ({len(horror_movies)} found):")
    print("-" * 40)
    
    for movie in horror_movies:
        print(f"• {movie['title']} ({movie['year']}) - {movie['director']}")
        print(f"  {movie['description'][:80]}...")
        
        youtube_data = simulate_youtube_search(movie)
        if youtube_data:
            print(f"  ✅ Available on YouTube ({youtube_data['duration']})")
        else:
            print(f"  ❌ Not on YouTube")
        print()


def demo_system_features():
    """Demo system features and capabilities."""
    print("\n🚀 System Features Demo")
    print("=" * 60)
    
    print("✨ Key Features:")
    print("• 🎭 Daily genre rotation (16 genres)")
    print("• 🔍 YouTube availability checking")
    print("• 🤖 AI-powered movie analysis (Gemini)")
    print("• 📊 LangGraph workflow orchestration")
    print("• 💾 Persistent recommendation storage")
    print("• 🌐 Web interface (Streamlit)")
    print("• 📅 Historical tracking")
    print("• 📈 Statistics and analytics")
    
    print(f"\n📚 Supported Genres:")
    for i, genre in enumerate(MOVIE_GENRES, 1):
        print(f"{i:2d}. {genre}")
    
    print(f"\n🎯 Focus: Classic movies from 1950-1980")
    print(f"🎬 Target: Movies available on YouTube")
    print(f"🔄 Rotation: Genre changes daily")
    
    sample_movies = load_sample_movies()
    if sample_movies:
        print(f"\n📊 Sample Data Statistics:")
        print(f"• Total movies in sample: {len(sample_movies)}")
        
        genres_count = {}
        for movie in sample_movies:
            genre = movie['genre']
            genres_count[genre] = genres_count.get(genre, 0) + 1
        
        print(f"• Genre distribution:")
        for genre, count in sorted(genres_count.items()):
            print(f"  - {genre}: {count} movies")


def main():
    """Run the demo."""
    print("🎬 Welcome to the Classic Movie Recommendation System Demo!")
    print("This demo shows how the system works using sample data.")
    print("For full functionality, set up API keys and run the real system.\n")
    
    # Run demos
    demo_daily_recommendations()
    demo_genre_recommendations()
    demo_system_features()
    
    print("\n" + "=" * 60)
    print("🎉 Demo Complete!")
    print("\nTo use the full system:")
    print("1. Get API keys:")
    print("   - Google Gemini: https://makersuite.google.com/app/apikey")
    print("   - YouTube Data API: https://console.cloud.google.com/")
    print("2. Copy .env.example to .env and add your keys")
    print("3. Install dependencies: pip install -r requirements.txt")
    print("4. Run: python main.py")
    print("5. Or web interface: streamlit run app.py")
    print("\n🧪 Test the system: python test_system.py")


if __name__ == "__main__":
    main()
