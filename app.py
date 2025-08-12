import streamlit as st
import pandas as pd
import numpy as np
from recommendation_engine import RecommendationEngine
from data_processor import DataProcessor
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="SmartSuggest - AI Recommendation System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .recommendation-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .similarity-score {
        font-weight: bold;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache the dataset"""
    processor = DataProcessor()
    movies_df, ratings_df = processor.load_sample_data()
    return movies_df, ratings_df

def main():
    # Header
    st.markdown('<h1 class="main-header">🎯 SmartSuggest</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">AI-Powered Recommendation System</p>', unsafe_allow_html=True)
    
    # Load data
    try:
        movies_df, ratings_df = load_data()
        engine = RecommendationEngine(movies_df, ratings_df)
        
        # Sidebar
        st.sidebar.header("🔧 Configuration")
        
        # Algorithm selection
        algorithm = st.sidebar.selectbox(
            "Choose Recommendation Algorithm",
            ["Content-Based", "Collaborative Filtering", "Hybrid"]
        )
        
        # Number of recommendations
        n_recommendations = st.sidebar.slider(
            "Number of Recommendations",
            min_value=5,
            max_value=20,
            value=10,
            step=1
        )
        
        # Main content
        tab1, tab2, tab3 = st.tabs(["🎬 Get Recommendations", "📊 Data Explorer", "🔍 System Info"])
        
        with tab1:
            st.header("Get Your Personalized Recommendations")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Movie selection
                st.subheader("Select Your Favorite Movies")
                
                # Search functionality
                search_term = st.text_input("🔍 Search for movies", "")
                
                if search_term:
                    filtered_movies = movies_df[
                        movies_df['title'].str.contains(search_term, case=False, na=False) |
                        movies_df['genres'].str.contains(search_term, case=False, na=False)
                    ]
                else:
                    filtered_movies = movies_df.head(20)
                
                selected_movies = st.multiselect(
                    "Choose movies you like:",
                    options=filtered_movies['title'].tolist(),
                    default=[],
                    key="movie_selection"
                )
                
                if st.button("🎯 Get Recommendations", type="primary"):
                    if selected_movies:
                        with st.spinner("Generating recommendations..."):
                            # Get movie IDs
                            selected_ids = movies_df[movies_df['title'].isin(selected_movies)]['movieId'].tolist()
                            
                            if algorithm == "Content-Based":
                                recommendations = engine.content_based_recommendations(selected_ids[0], n_recommendations)
                            elif algorithm == "Collaborative Filtering":
                                recommendations = engine.collaborative_filtering_recommendations(selected_ids, n_recommendations)
                            else:  # Hybrid
                                recommendations = engine.hybrid_recommendations(selected_ids, n_recommendations)
                            
                            # Display recommendations
                            st.subheader("🌟 Your Recommendations")
                            
                            for idx, (_, movie) in enumerate(recommendations.iterrows(), 1):
                                with st.container():
                                    st.markdown(f"""
                                    <div class="recommendation-card">
                                        <h4>#{idx} {movie['title']} ({movie.get('year', 'N/A')})</h4>
                                        <p><strong>Genres:</strong> {movie['genres']}</p>
                                        <p class="similarity-score">Similarity Score: {movie.get('similarity_score', 0):.3f}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                    else:
                        st.warning("Please select at least one movie to get recommendations.")
            
            with col2:
                st.subheader("📈 Algorithm Info")
                
                if algorithm == "Content-Based":
                    st.info("""
                    **Content-Based Filtering**
                    - Analyzes movie genres and features
                    - Uses TF-IDF vectorization
                    - Calculates cosine similarity
                    - Recommends similar movies
                    """)
                elif algorithm == "Collaborative Filtering":
                    st.info("""
                    **Collaborative Filtering**
                    - Uses user rating patterns
                    - Finds similar users/items
                    - K-Nearest Neighbors algorithm
                    - Community-based recommendations
                    """)
                else:
                    st.info("""
                    **Hybrid Approach**
                    - Combines both methods
                    - Weighted recommendation scores
                    - More robust predictions
                    - Best of both worlds
                    """)
        
        with tab2:
            st.header("📊 Dataset Explorer")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Movies", len(movies_df))
            with col2:
                st.metric("Total Ratings", len(ratings_df))
            with col3:
                st.metric("Unique Users", ratings_df['userId'].nunique())
            
            # Genre distribution
            st.subheader("🎭 Genre Distribution")
            genre_counts = {}
            for genres_str in movies_df['genres'].dropna():
                for genre in genres_str.split('|'):
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
            
            genre_df = pd.DataFrame(list(genre_counts.items()), columns=['Genre', 'Count'])
            genre_df = genre_df.sort_values('Count', ascending=False).head(10)
            
            fig = px.bar(genre_df, x='Genre', y='Count', title="Top 10 Movie Genres")
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Rating distribution
            st.subheader("⭐ Rating Distribution")
            fig2 = px.histogram(ratings_df, x='rating', nbins=10, title="Distribution of Movie Ratings")
            st.plotly_chart(fig2, use_container_width=True)
            
            # Sample data preview
            st.subheader("🎬 Sample Movies")
            st.dataframe(movies_df.head(10), use_container_width=True)
        
        with tab3:
            st.header("🔍 System Information")
            
            st.subheader("🧠 How It Works")
            
            st.markdown("""
            ### Content-Based Filtering
            1. **Feature Extraction**: Converts movie genres into TF-IDF vectors
            2. **Similarity Calculation**: Uses cosine similarity between movies
            3. **Recommendation**: Finds movies most similar to user preferences
            
            ### Collaborative Filtering  
            1. **User-Item Matrix**: Creates rating matrix from user behavior
            2. **Similarity Finding**: Uses KNN to find similar users/items
            3. **Prediction**: Recommends based on similar users' preferences
            
            ### Hybrid Approach
            1. **Combination**: Merges both content and collaborative scores
            2. **Weighting**: Balances different recommendation signals
            3. **Final Ranking**: Provides more robust recommendations
            """)
            
            st.subheader("📋 Technical Stack")
            st.markdown("""
            - **Frontend**: Streamlit
            - **ML Libraries**: Scikit-learn, Pandas, NumPy
            - **Algorithms**: TF-IDF, Cosine Similarity, K-Nearest Neighbors
            - **Visualization**: Plotly
            """)
            
    except Exception as e:
        st.error(f"Error loading the application: {str(e)}")
        st.info("Please ensure all required files are present and the data is properly formatted.")

if __name__ == "__main__":
    main()