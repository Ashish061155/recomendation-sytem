from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
from recommendation_engine import RecommendationEngine
from data_processor import DataProcessor
import os

app = Flask(__name__)
CORS(app)

# Global variables to store data and engine
movies_df = None
ratings_df = None
engine = None

def initialize_data():
    """Initialize the recommendation engine with data"""
    global movies_df, ratings_df, engine
    
    try:
        processor = DataProcessor()
        movies_df, ratings_df = processor.load_sample_data()
        engine = RecommendationEngine(movies_df, ratings_df)
        print("Recommendation engine initialized successfully")
    except Exception as e:
        print(f"Error initializing data: {e}")

@app.route('/')
def serve_index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS, etc.)"""
    return send_from_directory('.', filename)

@app.route('/api/movies')
def get_movies():
    """Get all movies"""
    if movies_df is None:
        return jsonify({'error': 'Data not initialized'}), 500
    
    movies_list = movies_df.to_dict('records')
    return jsonify(movies_list)

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get recommendations based on selected movies and algorithm"""
    if engine is None:
        return jsonify({'error': 'Recommendation engine not initialized'}), 500
    
    try:
        data = request.get_json()
        movie_ids = data.get('movie_ids', [])
        algorithm = data.get('algorithm', 'content')
        n_recommendations = data.get('n_recommendations', 10)
        
        if not movie_ids:
            return jsonify({'error': 'No movie IDs provided'}), 400
        
        # Generate recommendations based on algorithm
        if algorithm == 'content':
            recommendations = engine.content_based_recommendations(movie_ids[0], n_recommendations)
        elif algorithm == 'collaborative':
            recommendations = engine.collaborative_filtering_recommendations(movie_ids, n_recommendations)
        elif algorithm == 'hybrid':
            recommendations = engine.hybrid_recommendations(movie_ids, n_recommendations)
        else:
            return jsonify({'error': 'Invalid algorithm'}), 400
        
        # Convert to list of dictionaries
        recommendations_list = recommendations.to_dict('records')
        return jsonify(recommendations_list)
        
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return jsonify({'error': 'Failed to generate recommendations'}), 500

@app.route('/api/stats')
def get_stats():
    """Get dataset statistics"""
    if movies_df is None or ratings_df is None:
        return jsonify({'error': 'Data not initialized'}), 500
    
    stats = {
        'total_movies': len(movies_df),
        'total_ratings': len(ratings_df),
        'total_users': ratings_df['userId'].nunique(),
        'avg_rating': float(ratings_df['rating'].mean()),
        'rating_distribution': ratings_df['rating'].value_counts().sort_index().to_dict()
    }
    
    return jsonify(stats)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'engine_ready': engine is not None})

if __name__ == '__main__':
    initialize_data()
    app.run(host='0.0.0.0', port=5000, debug=True)