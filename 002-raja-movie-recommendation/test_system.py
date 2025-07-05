#!/usr/bin/env python3
"""
Test script for the Classic Movie Recommendation System
"""

import os
import sys
from datetime import datetime
from config import GOOGLE_API_KEY, YOUTUBE_API_KEY


def test_environment():
    """Test environment setup and API keys."""
    print("🧪 Testing Environment Setup")
    print("=" * 50)
    
    # Check API keys
    if not GOOGLE_API_KEY:
        print("❌ GOOGLE_API_KEY not found in environment")
        print("   Please set your Gemini API key in .env file")
        return False
    else:
        print("✅ Google API key found")
    
    if not YOUTUBE_API_KEY:
        print("⚠️  YOUTUBE_API_KEY not found (optional)")
        print("   YouTube search will use basic search without API")
    else:
        print("✅ YouTube API key found")
    
    return True


def test_youtube_search():
    """Test YouTube search functionality."""
    print("\n🔍 Testing YouTube Search")
    print("=" * 50)
    
    try:
        from youtube_search import YouTubeSearcher
        
        searcher = YouTubeSearcher()
        
        # Test with the example movie
        print("Searching for: The President's Plane Is Missing (1973)")
        results = searcher.search_movie("The President's Plane Is Missing", 1973)
        
        if results:
            print(f"✅ Found {len(results)} results")
            best_match = searcher.get_best_match("The President's Plane Is Missing", 1973)
            if best_match:
                print(f"✅ Best match: {best_match['title']}")
                print(f"   Duration: {best_match['duration']}")
                print(f"   URL: {best_match['url']}")
            else:
                print("⚠️  No best match found")
        else:
            print("❌ No results found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ YouTube search test failed: {str(e)}")
        return False


def test_movie_agent():
    """Test the movie recommendation agent."""
    print("\n🤖 Testing Movie Agent")
    print("=" * 50)
    
    try:
        from movie_agent import MovieRecommendationAgent
        
        agent = MovieRecommendationAgent()
        
        # Test genre selection
        print("Testing genre-specific recommendations...")
        recommendations = agent.get_genre_recommendations("Thriller")
        
        if recommendations:
            print(f"✅ Generated {len(recommendations)} thriller recommendations")
            for i, movie in enumerate(recommendations[:2], 1):  # Show first 2
                print(f"   {i}. {movie['title']} ({movie['year']})")
                if movie.get('youtube_data'):
                    print(f"      ✅ Available on YouTube")
                else:
                    print(f"      ❌ Not found on YouTube")
        else:
            print("❌ No recommendations generated")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Movie agent test failed: {str(e)}")
        return False


def test_utils():
    """Test utility functions."""
    print("\n🛠️  Testing Utilities")
    print("=" * 50)
    
    try:
        from utils import (
            ensure_data_directory, save_recommendations, 
            load_recommendations, get_genre_for_date
        )
        
        # Test data directory creation
        ensure_data_directory()
        print("✅ Data directory created/verified")
        
        # Test genre rotation
        today_genre = get_genre_for_date()
        print(f"✅ Today's genre: {today_genre}")
        
        # Test saving/loading recommendations
        test_recommendations = [
            {
                "title": "Test Movie",
                "year": 1970,
                "description": "A test movie for the system",
                "genre_analysis": "Test genre analysis",
                "cast_crew": "Test cast"
            }
        ]
        
        test_date = "2025-01-01"
        save_recommendations(test_recommendations, test_date)
        print("✅ Recommendations saved")
        
        loaded_recommendations = load_recommendations(test_date)
        if loaded_recommendations and len(loaded_recommendations) == 1:
            print("✅ Recommendations loaded successfully")
        else:
            print("❌ Failed to load recommendations")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Utils test failed: {str(e)}")
        return False


def test_full_workflow():
    """Test the complete workflow."""
    print("\n🔄 Testing Full Workflow")
    print("=" * 50)
    
    try:
        from main import MovieRecommendationSystem
        
        system = MovieRecommendationSystem()
        
        print("Generating daily recommendations...")
        recommendations = system.generate_daily_recommendations()
        
        if recommendations:
            print(f"✅ Generated {len(recommendations)} daily recommendations")
            
            # Check if recommendations have YouTube data
            youtube_count = sum(1 for movie in recommendations if movie.get('youtube_data'))
            print(f"✅ {youtube_count}/{len(recommendations)} movies found on YouTube")
            
            return True
        else:
            print("❌ No daily recommendations generated")
            return False
        
    except Exception as e:
        print(f"❌ Full workflow test failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("🎬 Classic Movie Recommendation System - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Environment Setup", test_environment),
        ("YouTube Search", test_youtube_search),
        ("Movie Agent", test_movie_agent),
        ("Utilities", test_utils),
        ("Full Workflow", test_full_workflow)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"\n❌ {test_name} test failed")
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Set up your API keys in .env file")
        print("2. Run: python main.py")
        print("3. Or run the web interface: streamlit run app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon issues:")
        print("- Missing API keys in .env file")
        print("- Internet connection problems")
        print("- Missing dependencies (run: pip install -r requirements.txt)")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
