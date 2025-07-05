import json
import requests
from typing import List, Dict, Optional
from youtubesearchpython import VideosSearch
from config import YOUTUBE_API_KEY, MAX_SEARCH_RESULTS, SEARCH_QUERY_TEMPLATE


class YouTubeSearcher:
    def __init__(self):
        self.api_key = YOUTUBE_API_KEY
        
    def search_movie(self, title: str, year: int) -> List[Dict]:
        """Search for a movie on YouTube and return video details."""
        query = SEARCH_QUERY_TEMPLATE.format(title=title, year=year)
        
        try:
            # Use youtube-search-python for basic search
            videos_search = VideosSearch(query, limit=MAX_SEARCH_RESULTS)
            results = videos_search.result()
            
            movies = []
            for video in results['result']:
                # Filter for longer videos (likely full movies)
                duration = self._parse_duration(video.get('duration', ''))
                if duration and duration > 60:  # At least 60 minutes
                    movie_data = {
                        'title': video['title'],
                        'url': video['link'],
                        'thumbnail': video['thumbnails'][0]['url'] if video['thumbnails'] else '',
                        'duration': video['duration'],
                        'channel': video['channel']['name'],
                        'views': video['viewCount']['text'] if video.get('viewCount') else 'N/A',
                        'published': video.get('publishedTime', 'N/A'),
                        'description': video.get('descriptionSnippet', [{}])[0].get('text', '') if video.get('descriptionSnippet') else ''
                    }
                    movies.append(movie_data)
            
            return movies
            
        except Exception as e:
            print(f"Error searching for {title} ({year}): {str(e)}")
            return []
    
    def _parse_duration(self, duration_str: str) -> Optional[int]:
        """Parse duration string and return minutes."""
        if not duration_str:
            return None
            
        try:
            # Handle formats like "1:30:45" or "45:30"
            parts = duration_str.split(':')
            if len(parts) == 3:  # hours:minutes:seconds
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 2:  # minutes:seconds
                return int(parts[0])
            else:
                return None
        except (ValueError, IndexError):
            return None
    
    def verify_movie_availability(self, title: str, year: int) -> bool:
        """Check if a movie is available on YouTube."""
        results = self.search_movie(title, year)
        return len(results) > 0
    
    def get_best_match(self, title: str, year: int) -> Optional[Dict]:
        """Get the best matching video for a movie."""
        results = self.search_movie(title, year)
        if not results:
            return None
            
        # Sort by duration (longer videos first) and views
        def score_video(video):
            duration = self._parse_duration(video['duration']) or 0
            # Simple scoring: prioritize longer videos
            return duration
            
        best_match = max(results, key=score_video)
        return best_match


def test_youtube_search():
    """Test the YouTube search functionality."""
    searcher = YouTubeSearcher()
    
    # Test with the example movie
    results = searcher.search_movie("The President's Plane Is Missing", 1973)
    print(f"Found {len(results)} results for 'The President's Plane Is Missing' (1973)")
    
    if results:
        best = searcher.get_best_match("The President's Plane Is Missing", 1973)
        print(f"Best match: {best['title']}")
        print(f"URL: {best['url']}")
        print(f"Duration: {best['duration']}")


if __name__ == "__main__":
    test_youtube_search()
