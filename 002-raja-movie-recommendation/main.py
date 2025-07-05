#!/usr/bin/env python3
"""
Classic Movie Recommendation System - Main Application
Daily movie recommendations for classic films (1950-1980) available on YouTube.
"""

import argparse
import schedule
import time
from datetime import datetime
from movie_agent import MovieRecommendationAgent
from utils import (
    save_recommendations, load_recommendations, 
    format_movie_for_display, get_genre_for_date, get_stats
)
from config import MOVIE_GENRES


class MovieRecommendationSystem:
    def __init__(self):
        self.agent = MovieRecommendationAgent()
    
    def generate_daily_recommendations(self, date: str = None):
        """Generate and save daily movie recommendations."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"🎬 Generating movie recommendations for {date}")
        print("=" * 50)
        
        # Check if recommendations already exist for today
        existing_recommendations = load_recommendations(date)
        if existing_recommendations:
            print(f"✅ Recommendations already exist for {date}")
            self.display_recommendations(existing_recommendations)
            return existing_recommendations
        
        try:
            # Generate new recommendations
            recommendations = self.agent.get_daily_recommendations()
            
            if not recommendations:
                print("❌ No recommendations generated. Please check your API keys and internet connection.")
                return []
            
            # Save recommendations
            save_recommendations(recommendations, date)
            
            print(f"✅ Generated {len(recommendations)} recommendations for {date}")
            self.display_recommendations(recommendations)
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Error generating recommendations: {str(e)}")
            return []
    
    def display_recommendations(self, recommendations):
        """Display movie recommendations in a formatted way."""
        if not recommendations:
            print("No recommendations to display.")
            return
        
        today_genre = get_genre_for_date()
        print(f"\n🎭 Today's Genre: {today_genre}")
        print("=" * 50)
        
        for i, movie in enumerate(recommendations, 1):
            print(f"\n{i}. 🎬 {movie['title']} ({movie['year']})")
            print("-" * 40)
            print(f"📝 {movie['description']}")
            
            if movie.get('genre_analysis'):
                print(f"\n🎭 Genre Analysis: {movie['genre_analysis']}")
            
            if movie.get('cast_crew'):
                print(f"👥 Cast & Crew: {movie['cast_crew']}")
            
            if movie.get('youtube_data'):
                youtube = movie['youtube_data']
                print(f"\n📺 YouTube: {youtube['title']}")
                print(f"🔗 URL: {youtube['url']}")
                print(f"⏱️ Duration: {youtube['duration']}")
                print(f"📺 Channel: {youtube['channel']}")
                if youtube.get('views') != 'N/A':
                    print(f"👀 Views: {youtube['views']}")
            
            print()
    
    def get_genre_recommendations(self, genre: str):
        """Get recommendations for a specific genre."""
        if genre not in MOVIE_GENRES:
            print(f"❌ Invalid genre. Available genres: {', '.join(MOVIE_GENRES)}")
            return []
        
        print(f"🎭 Generating {genre} movie recommendations...")
        print("=" * 50)
        
        try:
            recommendations = self.agent.get_genre_recommendations(genre)
            
            if recommendations:
                print(f"✅ Found {len(recommendations)} {genre} movies")
                self.display_recommendations(recommendations)
            else:
                print(f"❌ No {genre} movies found on YouTube")
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Error generating {genre} recommendations: {str(e)}")
            return []
    
    def show_stats(self):
        """Display system statistics."""
        stats = get_stats()
        
        print("📊 Movie Recommendation System Statistics")
        print("=" * 50)
        print(f"📅 Total days with recommendations: {stats['total_days']}")
        print(f"🎬 Total movies recommended: {stats['total_movies_recommended']}")
        print(f"💾 Movies in database: {stats['movies_in_database']}")
        
        if stats['last_recommendation_date']:
            print(f"📆 Last recommendation date: {stats['last_recommendation_date']}")
        
        print(f"\n🎭 Available genres: {', '.join(MOVIE_GENRES)}")
        print(f"📅 Today's genre: {get_genre_for_date()}")
    
    def run_scheduler(self):
        """Run the daily recommendation scheduler."""
        print("🕐 Starting daily movie recommendation scheduler...")
        print("Recommendations will be generated daily at 9:00 AM")
        
        # Schedule daily recommendations
        schedule.every().day.at("09:00").do(self.generate_daily_recommendations)
        
        # Generate today's recommendations if they don't exist
        today = datetime.now().strftime("%Y-%m-%d")
        if not load_recommendations(today):
            print("Generating initial recommendations...")
            self.generate_daily_recommendations()
        
        print("✅ Scheduler started. Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n👋 Scheduler stopped.")


def main():
    parser = argparse.ArgumentParser(
        description="Classic Movie Recommendation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Generate today's recommendations
  python main.py --genre Thriller   # Get thriller recommendations
  python main.py --stats            # Show system statistics
  python main.py --schedule         # Run daily scheduler
        """
    )
    
    parser.add_argument(
        '--genre', 
        choices=MOVIE_GENRES,
        help='Generate recommendations for a specific genre'
    )
    
    parser.add_argument(
        '--stats', 
        action='store_true',
        help='Show system statistics'
    )
    
    parser.add_argument(
        '--schedule', 
        action='store_true',
        help='Run the daily recommendation scheduler'
    )
    
    parser.add_argument(
        '--date',
        help='Generate recommendations for a specific date (YYYY-MM-DD)'
    )
    
    args = parser.parse_args()
    
    system = MovieRecommendationSystem()
    
    if args.stats:
        system.show_stats()
    elif args.genre:
        system.get_genre_recommendations(args.genre)
    elif args.schedule:
        system.run_scheduler()
    else:
        system.generate_daily_recommendations(args.date)


if __name__ == "__main__":
    main()
