import pandas as pd
import numpy as np
import requests
import json
import os

class DataProcessor:
    def __init__(self):
        """
        Initialize the data processor
        """
        self.movies_df = None
        self.ratings_df = None
    
    def load_sample_data(self):
        """
        Create sample movie and rating data for demonstration
        """
        # Create sample movies data
        movies_data = {
            'movieId': list(range(1, 101)),
            'title': [
                "The Shawshank Redemption", "The Godfather", "The Dark Knight", 
                "Pulp Fiction", "Forrest Gump", "Inception", "The Matrix",
                "Goodfellas", "The Silence of the Lambs", "Schindler's List",
                "Titanic", "Avatar", "Avengers: Endgame", "Spider-Man: No Way Home",
                "Top Gun: Maverick", "Black Panther", "The Lion King", "Toy Story",
                "Finding Nemo", "The Incredibles", "Frozen", "Moana", "Coco",
                "Inside Out", "Up", "WALL-E", "Ratatouille", "Monsters, Inc.",
                "The Departed", "Casino", "Heat", "Scarface", "The Irishman",
                "Once Upon a Time in Hollywood", "Django Unchained", "Kill Bill",
                "Interstellar", "Gravity", "Blade Runner 2049", "Mad Max: Fury Road",
                "John Wick", "Mission: Impossible", "Fast & Furious", "Transformers",
                "Star Wars: A New Hope", "Star Wars: The Empire Strikes Back",
                "Star Wars: Return of the Jedi", "The Lord of the Rings: Fellowship",
                "The Lord of the Rings: Two Towers", "The Lord of the Rings: Return",
                "Harry Potter: Sorcerer's Stone", "Harry Potter: Chamber of Secrets",
                "The Avengers", "Iron Man", "Thor", "Captain America", "Black Widow",
                "Doctor Strange", "Guardians of the Galaxy", "Ant-Man", "Spider-Man",
                "Batman Begins", "The Dark Knight Rises", "Wonder Woman", "Aquaman",
                "Justice League", "Man of Steel", "Superman", "Batman",
                "Joker", "Deadpool", "X-Men", "Wolverine", "Fantastic Four",
                "The Fantastic Beasts", "Pirates of the Caribbean", "Indiana Jones",
                "Jurassic Park", "Jurassic World", "King Kong", "Godzilla",
                "Pacific Rim", "Alien", "Predator", "Terminator", "RoboCop",
                "The Matrix Reloaded", "The Matrix Revolutions", "Back to the Future",
                "Ghostbusters", "Men in Black", "Independence Day", "War of the Worlds",
                "E.T.", "Close Encounters", "Contact", "Arrival", "Interstellar 2",
                "The Martian", "Apollo 13", "First Man", "Hidden Figures",
                "Ford v Ferrari", "Rush", "Le Mans '66", "Speed", "Gone in 60 Seconds"
            ],
            'genres': [
                "Drama", "Crime|Drama", "Action|Crime|Drama", "Crime|Drama",
                "Drama|Romance", "Action|Sci-Fi", "Action|Sci-Fi", "Crime|Drama",
                "Crime|Horror|Thriller", "Biography|Drama|History", "Drama|Romance",
                "Action|Adventure|Fantasy", "Action|Adventure|Drama", "Action|Adventure|Fantasy",
                "Action|Drama", "Action|Adventure|Sci-Fi", "Animation|Adventure|Drama",
                "Animation|Adventure|Comedy", "Animation|Adventure|Family", "Animation|Action|Adventure",
                "Animation|Adventure|Comedy", "Animation|Adventure|Comedy", "Animation|Adventure|Family",
                "Animation|Adventure|Comedy", "Animation|Adventure|Comedy", "Animation|Adventure|Drama",
                "Animation|Comedy|Family", "Animation|Comedy|Family", "Crime|Drama|Thriller",
                "Crime|Drama", "Action|Crime|Thriller", "Crime|Drama", "Crime|Drama",
                "Comedy|Drama", "Western", "Action|Crime|Thriller", "Drama|Sci-Fi",
                "Drama|Thriller", "Sci-Fi|Thriller", "Action|Adventure|Sci-Fi",
                "Action|Crime|Thriller", "Action|Adventure|Thriller", "Action|Crime|Thriller",
                "Action|Sci-Fi", "Adventure|Fantasy|Sci-Fi", "Adventure|Fantasy|Sci-Fi",
                "Adventure|Fantasy|Sci-Fi", "Adventure|Drama|Fantasy", "Adventure|Drama|Fantasy",
                "Adventure|Drama|Fantasy", "Adventure|Family|Fantasy", "Adventure|Family|Fantasy",
                "Action|Adventure|Sci-Fi", "Action|Adventure|Sci-Fi", "Action|Adventure|Fantasy",
                "Action|Adventure|Sci-Fi", "Action|Adventure|Thriller", "Adventure|Fantasy|Sci-Fi",
                "Action|Adventure|Comedy", "Action|Comedy|Sci-Fi", "Action|Adventure|Sci-Fi",
                "Action|Crime|Thriller", "Action|Adventure|Sci-Fi", "Action|Adventure|Fantasy",
                "Action|Adventure|Sci-Fi", "Action|Adventure|Sci-Fi", "Action|Adventure|Sci-Fi",
                "Action|Adventure|Sci-Fi", "Action|Adventure|Sci-Fi", "Crime|Drama|Thriller",
                "Action|Comedy|Sci-Fi", "Action|Sci-Fi", "Action|Adventure|Sci-Fi",
                "Action|Sci-Fi", "Adventure|Family|Fantasy", "Action|Adventure|Fantasy",
                "Adventure|Action", "Adventure|Action|Thriller", "Adventure|Action|Thriller",
                "Adventure|Sci-Fi", "Adventure|Sci-Fi", "Action|Sci-Fi", "Action|Sci-Fi",
                "Action|Sci-Fi", "Action|Sci-Fi", "Sci-Fi|Thriller", "Action|Sci-Fi",
                "Action|Adventure|Sci-Fi", "Adventure|Family|Sci-Fi", "Action|Comedy|Sci-Fi",
                "Action|Sci-Fi", "Action|Adventure|Sci-Fi", "Drama|Sci-Fi", "Sci-Fi|Thriller",
                "Drama|Sci-Fi", "Sci-Fi|Thriller", "Drama|Sci-Fi", "Drama|Sci-Fi",
                "Adventure|Drama|Sci-Fi", "Drama|History", "Biography|Drama", "Biography|Drama|Sport",
                "Biography|Drama|Sport", "Biography|Drama|Sport", "Action|Thriller", "Action|Crime|Thriller"
            ]
        }
        
        self.movies_df = pd.DataFrame(movies_data)
        
        # Extract year from title (simplified approach)
        self.movies_df['year'] = np.random.randint(1990, 2024, size=len(self.movies_df))
        
        # Create sample ratings data
        np.random.seed(42)  # For reproducible results
        n_users = 1000
        n_ratings = 10000
        
        ratings_data = {
            'userId': np.random.randint(1, n_users + 1, n_ratings),
            'movieId': np.random.choice(self.movies_df['movieId'], n_ratings),
            'rating': np.random.choice([1, 2, 3, 4, 5], n_ratings, p=[0.05, 0.1, 0.2, 0.35, 0.3]),
            'timestamp': np.random.randint(1000000000, 1700000000, n_ratings)
        }
        
        self.ratings_df = pd.DataFrame(ratings_data)
        
        # Remove duplicate user-movie combinations
        self.ratings_df = self.ratings_df.drop_duplicates(subset=['userId', 'movieId'])
        
        return self.movies_df, self.ratings_df
    
    def load_from_csv(self, movies_path, ratings_path):
        """
        Load data from CSV files (MoviesLens format)
        """
        try:
            self.movies_df = pd.read_csv(movies_path)
            self.ratings_df = pd.read_csv(ratings_path)
            
            # Ensure required columns exist
            required_movie_cols = ['movieId', 'title', 'genres']
            required_rating_cols = ['userId', 'movieId', 'rating']
            
            if not all(col in self.movies_df.columns for col in required_movie_cols):
                raise ValueError(f"Movies CSV must contain columns: {required_movie_cols}")
            
            if not all(col in self.ratings_df.columns for col in required_rating_cols):
                raise ValueError(f"Ratings CSV must contain columns: {required_rating_cols}")
            
            return self.movies_df, self.ratings_df
            
        except FileNotFoundError as e:
            print(f"File not found: {e}")
            return None, None
        except Exception as e:
            print(f"Error loading CSV files: {e}")
            return None, None
    
    def preprocess_data(self):
        """
        Clean and preprocess the loaded data
        """
        if self.movies_df is None or self.ratings_df is None:
            print("No data loaded. Please load data first.")
            return None, None
        
        # Clean movies data
        self.movies_df = self.movies_df.dropna(subset=['movieId', 'title'])
        self.movies_df['genres'] = self.movies_df['genres'].fillna('Unknown')
        
        # Clean ratings data
        self.ratings_df = self.ratings_df.dropna(subset=['userId', 'movieId', 'rating'])
        
        # Remove ratings for movies not in movies dataframe
        valid_movie_ids = self.movies_df['movieId'].unique()
        self.ratings_df = self.ratings_df[self.ratings_df['movieId'].isin(valid_movie_ids)]
        
        # Ensure rating values are in valid range
        self.ratings_df = self.ratings_df[
            (self.ratings_df['rating'] >= 0) & (self.ratings_df['rating'] <= 5)
        ]
        
        return self.movies_df, self.ratings_df
    
    def get_data_statistics(self):
        """
        Get basic statistics about the loaded data
        """
        if self.movies_df is None or self.ratings_df is None:
            return None
        
        stats = {
            'n_movies': len(self.movies_df),
            'n_ratings': len(self.ratings_df),
            'n_users': self.ratings_df['userId'].nunique(),
            'avg_rating': self.ratings_df['rating'].mean(),
            'rating_distribution': self.ratings_df['rating'].value_counts().sort_index(),
            'sparsity': 1 - (len(self.ratings_df) / (self.ratings_df['userId'].nunique() * len(self.movies_df)))
        }
        
        return stats
    
    def export_recommendations(self, recommendations, filename, format='csv'):
        """
        Export recommendations to file
        """
        try:
            if format.lower() == 'csv':
                recommendations.to_csv(filename, index=False)
            elif format.lower() == 'json':
                recommendations.to_json(filename, orient='records', indent=2)
            else:
                raise ValueError("Format must be 'csv' or 'json'")
            
            print(f"Recommendations exported to {filename}")
            return True
            
        except Exception as e:
            print(f"Error exporting recommendations: {e}")
            return False