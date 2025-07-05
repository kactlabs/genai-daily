import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from movie_agent import MovieRecommendationAgent
from utils import (
    load_recommendations, save_recommendations, 
    format_movie_for_display, get_genre_for_date, get_stats,
    export_recommendations_csv
)
from config import MOVIE_GENRES


# Page configuration
st.set_page_config(
    page_title="Classic Movie Recommendations",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .movie-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #ff6b6b;
    }
    .genre-badge {
        background-color: #4ecdc4;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
    }
    .youtube-link {
        background-color: #ff0000;
        color: white;
        padding: 8px 16px;
        border-radius: 5px;
        text-decoration: none;
        display: inline-block;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)


class StreamlitMovieApp:
    def __init__(self):
        self.agent = MovieRecommendationAgent()
    
    def render_movie_card(self, movie, index):
        """Render a movie recommendation card."""
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### 🎬 {movie['title']} ({movie['year']})")
                st.markdown(f"**Description:** {movie['description']}")
                
                if movie.get('genre_analysis'):
                    st.markdown(f"**🎭 Genre Analysis:** {movie['genre_analysis']}")
                
                if movie.get('cast_crew'):
                    st.markdown(f"**👥 Cast & Crew:** {movie['cast_crew']}")
            
            with col2:
                if movie.get('youtube_data'):
                    youtube = movie['youtube_data']
                    st.image(youtube.get('thumbnail', ''), width=200)
                    
                    st.markdown(f"**⏱️ Duration:** {youtube.get('duration', 'Unknown')}")
                    st.markdown(f"**📺 Channel:** {youtube.get('channel', 'Unknown')}")
                    
                    if youtube.get('views') != 'N/A':
                        st.markdown(f"**👀 Views:** {youtube.get('views', 'Unknown')}")
                    
                    # YouTube link button
                    st.markdown(
                        f'<a href="{youtube.get("url", "#")}" target="_blank" class="youtube-link">▶️ Watch on YouTube</a>',
                        unsafe_allow_html=True
                    )
            
            st.markdown("---")
    
    def main_page(self):
        """Main page with daily recommendations."""
        st.title("🎬 Classic Movie Recommendations")
        st.markdown("*Daily recommendations for classic movies (1950-1980) available on YouTube*")
        
        # Today's genre
        today_genre = get_genre_for_date()
        st.markdown(f"### 🎭 Today's Genre: {today_genre}")
        
        # Date selector
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            selected_date = st.date_input(
                "Select Date",
                value=datetime.now().date(),
                help="Choose a date to view recommendations"
            )
        
        with col2:
            if st.button("🎲 Generate New", help="Generate new recommendations for selected date"):
                with st.spinner("Generating recommendations..."):
                    try:
                        date_str = selected_date.strftime("%Y-%m-%d")
                        recommendations = self.agent.get_daily_recommendations()
                        save_recommendations(recommendations, date_str)
                        st.success(f"Generated {len(recommendations)} new recommendations!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating recommendations: {str(e)}")
        
        with col3:
            if st.button("📊 Show Stats"):
                st.session_state.show_stats = True
        
        # Load and display recommendations
        date_str = selected_date.strftime("%Y-%m-%d")
        recommendations = load_recommendations(date_str)
        
        if recommendations:
            st.markdown(f"### 📅 Recommendations for {selected_date}")
            
            for i, movie in enumerate(recommendations):
                self.render_movie_card(movie, i)
        else:
            st.info(f"No recommendations found for {selected_date}. Click 'Generate New' to create some!")
        
        # Show stats if requested
        if st.session_state.get('show_stats', False):
            self.show_stats_section()
            st.session_state.show_stats = False
    
    def genre_page(self):
        """Genre-specific recommendations page."""
        st.title("🎭 Genre-Specific Recommendations")
        
        # Genre selector
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_genre = st.selectbox(
                "Select Genre",
                options=MOVIE_GENRES,
                help="Choose a genre to get specific recommendations"
            )
        
        with col2:
            if st.button("🔍 Get Recommendations"):
                with st.spinner(f"Finding {selected_genre} movies..."):
                    try:
                        recommendations = self.agent.get_genre_recommendations(selected_genre)
                        st.session_state.genre_recommendations = recommendations
                        st.session_state.selected_genre = selected_genre
                    except Exception as e:
                        st.error(f"Error getting {selected_genre} recommendations: {str(e)}")
        
        # Display genre recommendations
        if st.session_state.get('genre_recommendations'):
            genre = st.session_state.get('selected_genre', selected_genre)
            recommendations = st.session_state.genre_recommendations
            
            st.markdown(f"### 🎬 {genre} Movies ({len(recommendations)} found)")
            
            for i, movie in enumerate(recommendations):
                self.render_movie_card(movie, i)
    
    def history_page(self):
        """Historical recommendations page."""
        st.title("📚 Recommendation History")
        
        # Load all recommendations
        from utils import load_all_recommendations
        all_recommendations = load_all_recommendations()
        
        if not all_recommendations:
            st.info("No recommendation history found. Generate some recommendations first!")
            return
        
        # Create DataFrame for display
        history_data = []
        for date, day_data in all_recommendations.items():
            for movie in day_data.get('recommendations', []):
                history_data.append({
                    'Date': date,
                    'Title': movie.get('title', ''),
                    'Year': movie.get('year', ''),
                    'Genre': get_genre_for_date(datetime.strptime(date, "%Y-%m-%d")),
                    'Available on YouTube': '✅' if movie.get('youtube_data') else '❌',
                    'Duration': movie.get('youtube_data', {}).get('duration', 'N/A')
                })
        
        if history_data:
            df = pd.DataFrame(history_data)
            
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                date_filter = st.selectbox(
                    "Filter by Date",
                    options=['All'] + sorted(df['Date'].unique(), reverse=True)
                )
            
            with col2:
                genre_filter = st.selectbox(
                    "Filter by Genre",
                    options=['All'] + sorted(df['Genre'].unique())
                )
            
            with col3:
                year_filter = st.selectbox(
                    "Filter by Year",
                    options=['All'] + sorted(df['Year'].unique())
                )
            
            # Apply filters
            filtered_df = df.copy()
            if date_filter != 'All':
                filtered_df = filtered_df[filtered_df['Date'] == date_filter]
            if genre_filter != 'All':
                filtered_df = filtered_df[filtered_df['Genre'] == genre_filter]
            if year_filter != 'All':
                filtered_df = filtered_df[filtered_df['Year'] == year_filter]
            
            # Display table
            st.dataframe(filtered_df, use_container_width=True)
            
            # Export option
            if st.button("📥 Export to CSV"):
                csv_file = export_recommendations_csv()
                st.success(f"Exported to {csv_file}")
        else:
            st.info("No recommendations found in history.")
    
    def show_stats_section(self):
        """Show system statistics."""
        stats = get_stats()
        
        st.markdown("### 📊 System Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Days", stats['total_days'])
        
        with col2:
            st.metric("Movies Recommended", stats['total_movies_recommended'])
        
        with col3:
            st.metric("Movies in Database", stats['movies_in_database'])
        
        with col4:
            if stats['last_recommendation_date']:
                st.metric("Last Update", stats['last_recommendation_date'])
    
    def sidebar(self):
        """Render sidebar navigation."""
        st.sidebar.title("🎬 Navigation")
        
        page = st.sidebar.radio(
            "Choose Page",
            ["🏠 Daily Recommendations", "🎭 By Genre", "📚 History"]
        )
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎯 Quick Actions")
        
        if st.sidebar.button("🎲 Random Genre"):
            import random
            random_genre = random.choice(MOVIE_GENRES)
            st.sidebar.success(f"Try: {random_genre}")
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ℹ️ About")
        st.sidebar.markdown("""
        This app recommends classic movies (1950-1980) 
        available on YouTube using AI-powered analysis.
        
        **Features:**
        - Daily genre rotation
        - YouTube availability check
        - AI-powered recommendations
        - Historical tracking
        """)
        
        return page
    
    def run(self):
        """Run the Streamlit app."""
        # Initialize session state
        if 'genre_recommendations' not in st.session_state:
            st.session_state.genre_recommendations = []
        
        # Sidebar navigation
        page = self.sidebar()
        
        # Route to appropriate page
        if page == "🏠 Daily Recommendations":
            self.main_page()
        elif page == "🎭 By Genre":
            self.genre_page()
        elif page == "📚 History":
            self.history_page()


def main():
    app = StreamlitMovieApp()
    app.run()


if __name__ == "__main__":
    main()
