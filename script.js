class RecommendationSystem {
    constructor() {
        this.movies = [];
        this.selectedMovies = new Set();
        this.currentAlgorithm = 'content';
        this.numRecommendations = 10;
        
        this.init();
    }

    async init() {
        await this.loadMovies();
        this.setupEventListeners();
        this.updateAlgorithmInfo();
        this.displayMovies();
        this.updateStats();
    }

    async loadMovies() {
        try {
            const response = await fetch('/api/movies');
            if (response.ok) {
                this.movies = await response.json();
            } else {
                // Fallback to sample data if API is not available
                this.movies = this.getSampleMovies();
            }
        } catch (error) {
            console.log('Using sample data');
            this.movies = this.getSampleMovies();
        }
    }

    getSampleMovies() {
        return [
            { movieId: 1, title: "The Shawshank Redemption", genres: "Drama", year: 1994 },
            { movieId: 2, title: "The Godfather", genres: "Crime|Drama", year: 1972 },
            { movieId: 3, title: "The Dark Knight", genres: "Action|Crime|Drama", year: 2008 },
            { movieId: 4, title: "Pulp Fiction", genres: "Crime|Drama", year: 1994 },
            { movieId: 5, title: "Forrest Gump", genres: "Drama|Romance", year: 1994 },
            { movieId: 6, title: "Inception", genres: "Action|Sci-Fi", year: 2010 },
            { movieId: 7, title: "The Matrix", genres: "Action|Sci-Fi", year: 1999 },
            { movieId: 8, title: "Goodfellas", genres: "Crime|Drama", year: 1990 },
            { movieId: 9, title: "The Silence of the Lambs", genres: "Crime|Horror|Thriller", year: 1991 },
            { movieId: 10, title: "Schindler's List", genres: "Biography|Drama|History", year: 1993 },
            { movieId: 11, title: "Titanic", genres: "Drama|Romance", year: 1997 },
            { movieId: 12, title: "Avatar", genres: "Action|Adventure|Fantasy", year: 2009 },
            { movieId: 13, title: "Avengers: Endgame", genres: "Action|Adventure|Drama", year: 2019 },
            { movieId: 14, title: "Spider-Man: No Way Home", genres: "Action|Adventure|Fantasy", year: 2021 },
            { movieId: 15, title: "Top Gun: Maverick", genres: "Action|Drama", year: 2022 },
            { movieId: 16, title: "Black Panther", genres: "Action|Adventure|Sci-Fi", year: 2018 },
            { movieId: 17, title: "The Lion King", genres: "Animation|Adventure|Drama", year: 1994 },
            { movieId: 18, title: "Toy Story", genres: "Animation|Adventure|Comedy", year: 1995 },
            { movieId: 19, title: "Finding Nemo", genres: "Animation|Adventure|Family", year: 2003 },
            { movieId: 20, title: "The Incredibles", genres: "Animation|Action|Adventure", year: 2004 },
            { movieId: 21, title: "Frozen", genres: "Animation|Adventure|Comedy", year: 2013 },
            { movieId: 22, title: "Moana", genres: "Animation|Adventure|Comedy", year: 2016 },
            { movieId: 23, title: "Coco", genres: "Animation|Adventure|Family", year: 2017 },
            { movieId: 24, title: "Inside Out", genres: "Animation|Adventure|Comedy", year: 2015 },
            { movieId: 25, title: "Up", genres: "Animation|Adventure|Comedy", year: 2009 },
            { movieId: 26, title: "WALL-E", genres: "Animation|Adventure|Drama", year: 2008 },
            { movieId: 27, title: "Ratatouille", genres: "Animation|Comedy|Family", year: 2007 },
            { movieId: 28, title: "Monsters, Inc.", genres: "Animation|Comedy|Family", year: 2001 },
            { movieId: 29, title: "The Departed", genres: "Crime|Drama|Thriller", year: 2006 },
            { movieId: 30, title: "Casino", genres: "Crime|Drama", year: 1995 }
        ];
    }

    setupEventListeners() {
        // Algorithm selection
        const algorithmSelect = document.getElementById('algorithm');
        algorithmSelect.addEventListener('change', (e) => {
            this.currentAlgorithm = e.target.value;
            this.updateAlgorithmInfo();
        });

        // Number of recommendations slider
        const slider = document.getElementById('numRecommendations');
        const sliderValue = document.getElementById('numValue');
        slider.addEventListener('input', (e) => {
            this.numRecommendations = parseInt(e.target.value);
            sliderValue.textContent = this.numRecommendations;
        });

        // Search functionality
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', (e) => {
            this.filterMovies(e.target.value);
        });

        // Get recommendations button
        const getRecommendationsBtn = document.getElementById('getRecommendations');
        getRecommendationsBtn.addEventListener('click', () => {
            this.getRecommendations();
        });
    }

    updateAlgorithmInfo() {
        const infoDiv = document.getElementById('algorithmInfo');
        const algorithms = {
            content: {
                title: 'Content-Based Filtering',
                points: [
                    'Analyzes movie genres and features',
                    'Uses TF-IDF vectorization',
                    'Calculates cosine similarity',
                    'Recommends similar movies'
                ]
            },
            collaborative: {
                title: 'Collaborative Filtering',
                points: [
                    'Uses user rating patterns',
                    'Finds similar users/items',
                    'K-Nearest Neighbors algorithm',
                    'Community-based recommendations'
                ]
            },
            hybrid: {
                title: 'Hybrid Approach',
                points: [
                    'Combines both methods',
                    'Weighted recommendation scores',
                    'More robust predictions',
                    'Best of both worlds'
                ]
            }
        };

        const algo = algorithms[this.currentAlgorithm];
        infoDiv.innerHTML = `
            <h4>${algo.title}</h4>
            <ul>
                ${algo.points.map(point => `<li>${point}</li>`).join('')}
            </ul>
        `;
    }

    displayMovies(moviesToShow = this.movies.slice(0, 20)) {
        const movieList = document.getElementById('movieList');
        movieList.innerHTML = '';

        moviesToShow.forEach(movie => {
            const movieCard = document.createElement('div');
            movieCard.className = `movie-card ${this.selectedMovies.has(movie.movieId) ? 'selected' : ''}`;
            movieCard.innerHTML = `
                <h4>${movie.title}</h4>
                <p>${movie.genres}</p>
                <small>${movie.year || 'N/A'}</small>
            `;

            movieCard.addEventListener('click', () => {
                this.toggleMovieSelection(movie);
            });

            movieList.appendChild(movieCard);
        });
    }

    filterMovies(searchTerm) {
        if (!searchTerm.trim()) {
            this.displayMovies();
            return;
        }

        const filtered = this.movies.filter(movie => 
            movie.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            movie.genres.toLowerCase().includes(searchTerm.toLowerCase())
        );

        this.displayMovies(filtered);
    }

    toggleMovieSelection(movie) {
        if (this.selectedMovies.has(movie.movieId)) {
            this.selectedMovies.delete(movie.movieId);
        } else {
            this.selectedMovies.add(movie.movieId);
        }

        this.updateSelectedMoviesDisplay();
        this.updateRecommendationButton();
        
        // Update movie card appearance
        const movieCards = document.querySelectorAll('.movie-card');
        movieCards.forEach(card => {
            const title = card.querySelector('h4').textContent;
            const movieData = this.movies.find(m => m.title === title);
            if (movieData) {
                card.className = `movie-card ${this.selectedMovies.has(movieData.movieId) ? 'selected' : ''}`;
            }
        });
    }

    updateSelectedMoviesDisplay() {
        const selectedDiv = document.getElementById('selectedMovies');
        
        if (this.selectedMovies.size === 0) {
            selectedDiv.innerHTML = '<p class="no-selection">No movies selected yet</p>';
            return;
        }

        const selectedMoviesList = Array.from(this.selectedMovies).map(movieId => {
            const movie = this.movies.find(m => m.movieId === movieId);
            return movie ? `
                <div class="selected-item">
                    ${movie.title}
                    <button class="remove-btn" onclick="recommendationSystem.removeSelectedMovie(${movieId})">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            ` : '';
        }).join('');

        selectedDiv.innerHTML = selectedMoviesList;
    }

    removeSelectedMovie(movieId) {
        this.selectedMovies.delete(movieId);
        this.updateSelectedMoviesDisplay();
        this.updateRecommendationButton();
        this.displayMovies();
    }

    updateRecommendationButton() {
        const button = document.getElementById('getRecommendations');
        button.disabled = this.selectedMovies.size === 0;
    }

    async getRecommendations() {
        const loadingSpinner = document.getElementById('loadingSpinner');
        const resultsSection = document.getElementById('resultsSection');
        
        loadingSpinner.style.display = 'block';
        resultsSection.style.display = 'none';

        try {
            // Simulate API call delay
            await new Promise(resolve => setTimeout(resolve, 1500));

            const selectedMovieIds = Array.from(this.selectedMovies);
            let recommendations;

            try {
                const response = await fetch('/api/recommendations', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        movie_ids: selectedMovieIds,
                        algorithm: this.currentAlgorithm,
                        n_recommendations: this.numRecommendations
                    })
                });

                if (response.ok) {
                    recommendations = await response.json();
                } else {
                    throw new Error('API not available');
                }
            } catch (error) {
                // Fallback to client-side recommendations
                recommendations = this.generateClientSideRecommendations(selectedMovieIds);
            }

            this.displayRecommendations(recommendations);
        } finally {
            loadingSpinner.style.display = 'none';
            resultsSection.style.display = 'block';
        }
    }

    generateClientSideRecommendations(selectedMovieIds) {
        const selectedMovies = selectedMovieIds.map(id => 
            this.movies.find(m => m.movieId === id)
        ).filter(Boolean);

        if (selectedMovies.length === 0) return [];

        // Simple content-based recommendation logic
        const selectedGenres = new Set();
        selectedMovies.forEach(movie => {
            movie.genres.split('|').forEach(genre => selectedGenres.add(genre.trim()));
        });

        const recommendations = this.movies
            .filter(movie => !selectedMovieIds.includes(movie.movieId))
            .map(movie => {
                const movieGenres = new Set(movie.genres.split('|').map(g => g.trim()));
                const intersection = new Set([...selectedGenres].filter(x => movieGenres.has(x)));
                const similarity = intersection.size / Math.max(selectedGenres.size, movieGenres.size);
                
                return {
                    ...movie,
                    similarity_score: similarity + Math.random() * 0.1 // Add some randomness
                };
            })
            .sort((a, b) => b.similarity_score - a.similarity_score)
            .slice(0, this.numRecommendations);

        return recommendations;
    }

    displayRecommendations(recommendations) {
        const recommendationsList = document.getElementById('recommendationsList');
        
        if (!recommendations || recommendations.length === 0) {
            recommendationsList.innerHTML = '<p>No recommendations found. Try selecting different movies.</p>';
            return;
        }

        recommendationsList.innerHTML = recommendations.map((movie, index) => `
            <div class="recommendation-card">
                <div class="rank">${index + 1}</div>
                <h4>${movie.title} ${movie.year ? `(${movie.year})` : ''}</h4>
                <p class="genres"><strong>Genres:</strong> ${movie.genres}</p>
                <div class="similarity-score">
                    Similarity Score: ${(movie.similarity_score || 0).toFixed(3)}
                </div>
            </div>
        `).join('');

        // Scroll to results
        document.getElementById('resultsSection').scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }

    updateStats() {
        document.getElementById('totalMovies').textContent = this.movies.length.toLocaleString();
        document.getElementById('totalRatings').textContent = '10,000';
        document.getElementById('totalUsers').textContent = '1,000';
    }
}

// Initialize the application
let recommendationSystem;
document.addEventListener('DOMContentLoaded', () => {
    recommendationSystem = new RecommendationSystem();
});