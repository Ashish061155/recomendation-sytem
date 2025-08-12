import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

class RecommendationUtils:
    """
    Utility functions for the recommendation system
    """
    
    @staticmethod
    def calculate_diversity(recommendations, movies_df):
        """
        Calculate diversity of recommendations based on genres
        """
        if recommendations.empty:
            return 0.0
        
        # Get genres for recommended movies
        rec_genres = []
        for _, movie in recommendations.iterrows():
            genres = movie['genres'].split('|') if pd.notna(movie['genres']) else []
            rec_genres.extend(genres)
        
        # Calculate unique genres ratio
        unique_genres = len(set(rec_genres))
        total_possible_genres = len(set('|'.join(movies_df['genres'].dropna()).split('|')))
        
        return unique_genres / total_possible_genres if total_possible_genres > 0 else 0.0
    
    @staticmethod
    def calculate_novelty(recommendations, ratings_df):
        """
        Calculate novelty of recommendations based on popularity
        """
        if recommendations.empty:
            return 0.0
        
        # Calculate movie popularity (number of ratings)
        movie_popularity = ratings_df.groupby('movieId').size()
        
        novelty_scores = []
        for _, movie in recommendations.iterrows():
            movie_id = movie['movieId']
            popularity = movie_popularity.get(movie_id, 0)
            # Higher novelty for less popular movies
            novelty = 1 / (1 + np.log(popularity + 1))
            novelty_scores.append(novelty)
        
        return np.mean(novelty_scores) if novelty_scores else 0.0
    
    @staticmethod
    def evaluate_recommendations(recommendations, test_ratings, movies_df):
        """
        Evaluate recommendation quality
        """
        metrics = {}
        
        # Diversity
        metrics['diversity'] = RecommendationUtils.calculate_diversity(recommendations, movies_df)
        
        # Novelty
        metrics['novelty'] = RecommendationUtils.calculate_novelty(recommendations, test_ratings)
        
        # Coverage (percentage of catalog recommended)
        total_movies = len(movies_df)
        recommended_movies = len(recommendations)
        metrics['coverage'] = recommended_movies / total_movies if total_movies > 0 else 0.0
        
        return metrics
    
    @staticmethod
    def format_movie_title(title, max_length=50):
        """
        Format movie title for display
        """
        if pd.isna(title):
            return "Unknown Title"
        
        if len(title) > max_length:
            return title[:max_length-3] + "..."
        return title
    
    @staticmethod
    def extract_year_from_title(title):
        """
        Extract year from movie title (format: "Title (Year)")
        """
        if pd.isna(title):
            return None
        
        try:
            # Look for year in parentheses at the end
            if '(' in title and ')' in title:
                year_part = title.split('(')[-1].split(')')[0]
                year = int(year_part)
                if 1900 <= year <= 2030:  # Reasonable year range
                    return year
        except:
            pass
        
        return None
    
    @staticmethod
    def get_genre_distribution(movies_df):
        """
        Get distribution of genres in the dataset
        """
        genre_counts = {}
        
        for genres_str in movies_df['genres'].dropna():
            for genre in genres_str.split('|'):
                if genre.strip():  # Ignore empty genres
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        return dict(sorted(genre_counts.items(), key=lambda x: x[1], reverse=True))
    
    @staticmethod
    def create_user_profile(user_ratings, movies_df):
        """
        Create a user profile based on their rating history
        """
        if user_ratings.empty:
            return {}
        
        # Merge ratings with movie information
        user_movies = user_ratings.merge(movies_df, on='movieId')
        
        # Calculate genre preferences
        genre_ratings = {}
        genre_counts = {}
        
        for _, movie in user_movies.iterrows():
            rating = movie['rating']
            genres = movie['genres'].split('|') if pd.notna(movie['genres']) else []
            
            for genre in genres:
                if genre.strip():
                    genre_ratings[genre] = genre_ratings.get(genre, 0) + rating
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        # Calculate average rating per genre
        genre_preferences = {}
        for genre in genre_ratings:
            genre_preferences[genre] = genre_ratings[genre] / genre_counts[genre]
        
        profile = {
            'total_ratings': len(user_ratings),
            'avg_rating': user_ratings['rating'].mean(),
            'rating_std': user_ratings['rating'].std(),
            'favorite_genres': sorted(genre_preferences.items(), key=lambda x: x[1], reverse=True)[:5],
            'rating_distribution': user_ratings['rating'].value_counts().sort_index().to_dict()
        }
        
        return profile
    
    @staticmethod
    def similarity_explanation(movie1_genres, movie2_genres):
        """
        Generate explanation for why two movies are similar
        """
        if pd.isna(movie1_genres) or pd.isna(movie2_genres):
            return "Limited genre information available"
        
        genres1 = set(movie1_genres.split('|'))
        genres2 = set(movie2_genres.split('|'))
        
        common_genres = genres1.intersection(genres2)
        
        if common_genres:
            return f"Similar genres: {', '.join(common_genres)}"
        else:
            return "Different genres - recommended based on user behavior patterns"
    
    @staticmethod
    def get_trending_movies(ratings_df, movies_df, time_window_days=30):
        """
        Get trending movies based on recent ratings
        """
        # Convert timestamp to datetime if it's not already
        if 'timestamp' in ratings_df.columns:
            ratings_df['datetime'] = pd.to_datetime(ratings_df['timestamp'], unit='s')
            
            # Filter recent ratings
            cutoff_date = ratings_df['datetime'].max() - pd.Timedelta(days=time_window_days)
            recent_ratings = ratings_df[ratings_df['datetime'] >= cutoff_date]
        else:
            # If no timestamp, use all ratings
            recent_ratings = ratings_df
        
        # Calculate trending score (combination of rating and frequency)
        trending_scores = recent_ratings.groupby('movieId').agg({
            'rating': ['mean', 'count']
        }).reset_index()
        
        trending_scores.columns = ['movieId', 'avg_rating', 'rating_count']
        
        # Calculate trending score (weighted by both rating and count)
        trending_scores['trending_score'] = (
            trending_scores['avg_rating'] * np.log(trending_scores['rating_count'] + 1)
        )
        
        # Merge with movie information
        trending_movies = trending_scores.merge(movies_df, on='movieId')
        trending_movies = trending_movies.sort_values('trending_score', ascending=False)
        
        return trending_movies