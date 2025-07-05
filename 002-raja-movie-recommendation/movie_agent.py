import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from config import (
    GOOGLE_API_KEY, MODEL_NAME, TEMPERATURE, MAX_TOKENS,
    MOVIE_GENRES, CLASSIC_MOVIE_YEARS, DAILY_RECOMMENDATION_COUNT
)
from youtube_search import YouTubeSearcher


class MovieRecommendationState(TypedDict):
    messages: List[BaseMessage]
    current_genre: str
    recommended_movies: List[Dict]
    search_results: List[Dict]
    final_recommendations: List[Dict]


class MovieRecommendationAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            google_api_key=GOOGLE_API_KEY
        )
        self.youtube_searcher = YouTubeSearcher()
        self.graph = self._create_graph()
        
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow for movie recommendations."""
        workflow = StateGraph(MovieRecommendationState)
        
        # Add nodes
        workflow.add_node("select_genre", self._select_genre)
        workflow.add_node("generate_movies", self._generate_movies)
        workflow.add_node("search_youtube", self._search_youtube)
        workflow.add_node("analyze_and_rank", self._analyze_and_rank)
        
        # Add edges
        workflow.set_entry_point("select_genre")
        workflow.add_edge("select_genre", "generate_movies")
        workflow.add_edge("generate_movies", "search_youtube")
        workflow.add_edge("search_youtube", "analyze_and_rank")
        workflow.add_edge("analyze_and_rank", END)
        
        return workflow.compile()
    
    def _select_genre(self, state: MovieRecommendationState) -> MovieRecommendationState:
        """Select today's genre based on date rotation."""
        today = datetime.now()
        genre_index = today.timetuple().tm_yday % len(MOVIE_GENRES)
        selected_genre = MOVIE_GENRES[genre_index]
        
        state["current_genre"] = selected_genre
        print(f"Selected genre for today: {selected_genre}")
        return state
    
    def _generate_movies(self, state: MovieRecommendationState) -> MovieRecommendationState:
        """Generate movie recommendations using Gemini."""
        genre = state["current_genre"]
        
        prompt = ChatPromptTemplate.from_template("""
        You are a classic movie expert specializing in films from 1950-1980.
        
        Generate {count} classic {genre} movies from 1950-1980 that are likely to be available on YouTube.
        Focus on lesser-known gems, B-movies, and public domain films that would be freely available.
        
        For each movie, provide:
        1. Title
        2. Year
        3. Brief description (2-3 sentences)
        4. Why it's a good example of {genre}
        5. Notable actors/director if any
        
        Format as JSON array with objects containing: title, year, description, genre_analysis, cast_crew
        
        Example format:
        [
            {{
                "title": "Movie Title",
                "year": 1973,
                "description": "Brief description of the plot and significance.",
                "genre_analysis": "Why this is a great example of the genre.",
                "cast_crew": "Notable actors and director"
            }}
        ]
        """)
        
        chain = prompt | self.llm
        response = chain.invoke({
            "genre": genre,
            "count": DAILY_RECOMMENDATION_COUNT + 2  # Generate extra for filtering
        })
        
        try:
            # Extract JSON from response
            content = response.content
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            else:
                json_str = content.strip()
            
            movies = json.loads(json_str)
            state["recommended_movies"] = movies
            print(f"Generated {len(movies)} movie recommendations")
            
        except (json.JSONDecodeError, IndexError) as e:
            print(f"Error parsing movie recommendations: {e}")
            # Fallback to manual parsing or default movies
            state["recommended_movies"] = self._get_fallback_movies(genre)
        
        return state
    
    def _search_youtube(self, state: MovieRecommendationState) -> MovieRecommendationState:
        """Search for movies on YouTube."""
        movies = state["recommended_movies"]
        search_results = []
        
        for movie in movies:
            print(f"Searching YouTube for: {movie['title']} ({movie['year']})")
            youtube_results = self.youtube_searcher.search_movie(movie['title'], movie['year'])
            
            if youtube_results:
                best_match = self.youtube_searcher.get_best_match(movie['title'], movie['year'])
                if best_match:
                    movie_with_youtube = {
                        **movie,
                        'youtube_data': best_match,
                        'available_on_youtube': True
                    }
                    search_results.append(movie_with_youtube)
                    print(f"✓ Found on YouTube: {best_match['title']}")
                else:
                    print(f"✗ No suitable match found for {movie['title']}")
            else:
                print(f"✗ Not found on YouTube: {movie['title']}")
        
        state["search_results"] = search_results
        return state
    
    def _analyze_and_rank(self, state: MovieRecommendationState) -> MovieRecommendationState:
        """Analyze and rank the final recommendations."""
        available_movies = state["search_results"]
        
        if len(available_movies) < DAILY_RECOMMENDATION_COUNT:
            print(f"Warning: Only found {len(available_movies)} movies on YouTube")
        
        # Sort by video quality indicators (duration, views, etc.)
        def score_movie(movie):
            youtube_data = movie.get('youtube_data', {})
            duration = self.youtube_searcher._parse_duration(youtube_data.get('duration', '')) or 0
            
            # Simple scoring: prefer longer videos (more likely to be complete movies)
            score = duration
            
            # Bonus for certain keywords in title that suggest full movie
            title_lower = youtube_data.get('title', '').lower()
            if 'full movie' in title_lower:
                score += 100
            if 'complete' in title_lower:
                score += 50
                
            return score
        
        # Select top recommendations
        sorted_movies = sorted(available_movies, key=score_movie, reverse=True)
        final_recommendations = sorted_movies[:DAILY_RECOMMENDATION_COUNT]
        
        state["final_recommendations"] = final_recommendations
        print(f"Final recommendations: {len(final_recommendations)} movies")
        
        return state
    
    def _get_fallback_movies(self, genre: str) -> List[Dict]:
        """Fallback movies if AI generation fails."""
        fallback_movies = {
            "Thriller": [
                {
                    "title": "The President's Plane Is Missing",
                    "year": 1973,
                    "description": "A political thriller about the disappearance of Air Force One.",
                    "genre_analysis": "Classic 70s political paranoia thriller.",
                    "cast_crew": "Buddy Ebsen, Peter Graves"
                }
            ],
            "Drama": [
                {
                    "title": "Marty",
                    "year": 1955,
                    "description": "A lonely butcher finds love in the Bronx.",
                    "genre_analysis": "Intimate character study of working-class life.",
                    "cast_crew": "Ernest Borgnine, Betsy Blair"
                }
            ]
        }
        
        return fallback_movies.get(genre, fallback_movies["Drama"])
    
    def get_daily_recommendations(self) -> List[Dict]:
        """Get today's movie recommendations."""
        initial_state = MovieRecommendationState(
            messages=[],
            current_genre="",
            recommended_movies=[],
            search_results=[],
            final_recommendations=[]
        )
        
        final_state = self.graph.invoke(initial_state)
        return final_state["final_recommendations"]
    
    def get_genre_recommendations(self, genre: str) -> List[Dict]:
        """Get recommendations for a specific genre."""
        initial_state = MovieRecommendationState(
            messages=[],
            current_genre=genre,
            recommended_movies=[],
            search_results=[],
            final_recommendations=[]
        )
        
        # Skip genre selection and start with movie generation
        state = self._generate_movies(initial_state)
        state = self._search_youtube(state)
        state = self._analyze_and_rank(state)
        
        return state["final_recommendations"]


def test_movie_agent():
    """Test the movie recommendation agent."""
    agent = MovieRecommendationAgent()
    
    print("Testing daily recommendations...")
    recommendations = agent.get_daily_recommendations()
    
    print(f"\nDaily Recommendations ({len(recommendations)} movies):")
    for i, movie in enumerate(recommendations, 1):
        print(f"\n{i}. {movie['title']} ({movie['year']})")
        print(f"   Description: {movie['description']}")
        if movie.get('youtube_data'):
            print(f"   YouTube: {movie['youtube_data']['url']}")
            print(f"   Duration: {movie['youtube_data']['duration']}")


if __name__ == "__main__":
    test_movie_agent()
