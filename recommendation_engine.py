import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import TruncatedSVD
import warnings
warnings.filterwarnings('ignore')

class RecommendationEngine:
    def __init__(self, movies_df, ratings_df):
        """
        Initialize the recommendation engine with movie and rating data
        """
        self.movies_df = movies_df.copy()
        self.ratings_df = ratings_df.copy()
        self.user_item_matrix = None
        self.content_similarity_matrix = None
        self.tfidf_vectorizer = None
        self.knn_model = None
        
        # Prepare data
        self._prepare_data()
    
    def _prepare_data(self):
        """
        Prepare data for recommendation algorithms
        """
        # Create user-item matrix for collaborative filtering
        self.user_item_matrix = self.ratings_df.pivot_table(
            index='userId',
            columns='movieId', 
            values='rating',
            fill_value=0
        )
        
        # Prepare content-based features
        self._prepare_content_features()
        
        # Prepare collaborative filtering model
        self._prepare_collaborative_model()
    
    def _prepare_content_features(self):
        """
        Prepare TF-IDF features for content-based filtering
        """
        # Fill missing genres
        self.movies_df['genres'] = self.movies_df['genres'].fillna('')
        
        # Create TF-IDF vectors from genres
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.movies_df['genres'])
        
        # Calculate cosine similarity matrix
        self.content_similarity_matrix = cosine_similarity(tfidf_matrix)
    
    def _prepare_collaborative_model(self):
        """
        Prepare KNN model for collaborative filtering
        """
        # Use matrix with movies as rows for item-based collaborative filtering
        movie_item_matrix = self.user_item_matrix.T
        
        # Fit KNN model
        self.knn_model = NearestNeighbors(
            metric='cosine',
            algorithm='brute',
            n_neighbors=20
        )
        
        # Only fit if we have enough data
        if movie_item_matrix.shape[0] > 0:
            self.knn_model.fit(movie_item_matrix.values)
    
    def content_based_recommendations(self, movie_id, n_recommendations=10):
        """
        Generate content-based recommendations for a given movie
        """
        try:
            # Find movie index in the dataframe
            movie_idx = self.movies_df[self.movies_df['movieId'] == movie_id].index[0]
            
            # Get similarity scores
            similarity_scores = list(enumerate(self.content_similarity_matrix[movie_idx]))
            
            # Sort by similarity (excluding the movie itself)
            similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[1:n_recommendations+1]
            
            # Get movie indices
            movie_indices = [i[0] for i in similarity_scores]
            similarity_values = [i[1] for i in similarity_scores]
            
            # Get recommended movies
            recommendations = self.movies_df.iloc[movie_indices].copy()
            recommendations['similarity_score'] = similarity_values
            
            return recommendations
            
        except IndexError:
            # If movie not found, return popular movies
            return self._get_popular_movies(n_recommendations)
    
    def collaborative_filtering_recommendations(self, movie_ids, n_recommendations=10):
        """
        Generate collaborative filtering recommendations based on multiple movies
        """
        try:
            recommendations_list = []
            
            for movie_id in movie_ids:
                if movie_id in self.user_item_matrix.columns:
                    # Find movie index in user_item_matrix
                    movie_idx = list(self.user_item_matrix.columns).index(movie_id)
                    
                    # Get similar movies using KNN
                    distances, indices = self.knn_model.kneighbors(
                        [self.user_item_matrix.T.iloc[movie_idx].values],
                        n_neighbors=min(n_recommendations + 1, len(self.user_item_matrix.columns))
                    )
                    
                    # Get similar movie IDs (excluding the input movie)
                    similar_movie_indices = indices.flatten()[1:]
                    similarity_scores = 1 - distances.flatten()[1:]  # Convert distance to similarity
                    
                    # Get movie IDs
                    similar_movie_ids = [self.user_item_matrix.columns[idx] for idx in similar_movie_indices]
                    
                    for i, movie_id in enumerate(similar_movie_ids):
                        movie_info = self.movies_df[self.movies_df['movieId'] == movie_id]
                        if not movie_info.empty:
                            movie_data = movie_info.iloc[0].to_dict()
                            movie_data['similarity_score'] = similarity_scores[i]
                            recommendations_list.append(movie_data)
            
            # Remove duplicates and sort by similarity score
            recommendations_df = pd.DataFrame(recommendations_list)
            if not recommendations_df.empty:
                recommendations_df = recommendations_df.drop_duplicates(subset=['movieId'])
                recommendations_df = recommendations_df.sort_values('similarity_score', ascending=False)
                return recommendations_df.head(n_recommendations)
            else:
                return self._get_popular_movies(n_recommendations)
                
        except Exception as e:
            print(f"Error in collaborative filtering: {e}")
            return self._get_popular_movies(n_recommendations)
    
    def hybrid_recommendations(self, movie_ids, n_recommendations=10, content_weight=0.6, collab_weight=0.4):
        """
        Generate hybrid recommendations combining content-based and collaborative filtering
        """
        hybrid_scores = {}
        
        # Get content-based recommendations
        if movie_ids:
            content_recs = self.content_based_recommendations(movie_ids[0], n_recommendations * 2)
            for _, movie in content_recs.iterrows():
                movie_id = movie['movieId']
                hybrid_scores[movie_id] = hybrid_scores.get(movie_id, 0) + (
                    content_weight * movie['similarity_score']
                )
        
        # Get collaborative filtering recommendations
        collab_recs = self.collaborative_filtering_recommendations(movie_ids, n_recommendations * 2)
        if not collab_recs.empty:
            for _, movie in collab_recs.iterrows():
                movie_id = movie['movieId']
                hybrid_scores[movie_id] = hybrid_scores.get(movie_id, 0) + (
                    collab_weight * movie['similarity_score']
                )
        
        # Sort by hybrid score
        sorted_movies = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)
        top_movie_ids = [movie_id for movie_id, _ in sorted_movies[:n_recommendations]]
        
        # Get movie details
        recommendations = []
        for movie_id in top_movie_ids:
            movie_info = self.movies_df[self.movies_df['movieId'] == movie_id]
            if not movie_info.empty:
                movie_data = movie_info.iloc[0].to_dict()
                movie_data['similarity_score'] = hybrid_scores[movie_id]
                recommendations.append(movie_data)
        
        return pd.DataFrame(recommendations) if recommendations else self._get_popular_movies(n_recommendations)
    
    def _get_popular_movies(self, n_recommendations=10):
        """
        Get popular movies as fallback recommendations
        """
        # Calculate average ratings
        avg_ratings = self.ratings_df.groupby('movieId')['rating'].agg(['mean', 'count']).reset_index()
        avg_ratings = avg_ratings[avg_ratings['count'] >= 10]  # At least 10 ratings
        
        # Merge with movie details
        popular_movies = avg_ratings.merge(self.movies_df, on='movieId')
        popular_movies = popular_movies.sort_values('mean', ascending=False)
        
        # Add similarity score for consistency
        popular_movies['similarity_score'] = popular_movies['mean'] / 5.0  # Normalize to 0-1
        
        return popular_movies.head(n_recommendations)
    
    def get_user_recommendations(self, user_id, n_recommendations=10):
        """
        Get recommendations for a specific user based on their rating history
        """
        if user_id not in self.user_item_matrix.index:
            return self._get_popular_movies(n_recommendations)
        
        # Get user's ratings
        user_ratings = self.user_item_matrix.loc[user_id]
        rated_movies = user_ratings[user_ratings > 0].index.tolist()
        
        # Get highly rated movies by the user
        high_rated_movies = user_ratings[user_ratings >= 4.0].index.tolist()
        
        if high_rated_movies:
            # Use collaborative filtering based on highly rated movies
            return self.collaborative_filtering_recommendations(high_rated_movies, n_recommendations)
        else:
            return self._get_popular_movies(n_recommendations)