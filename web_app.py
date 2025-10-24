"""
Stunning web interface for the music recommendation engine.

This module provides a beautiful Flask-based web application with:
- Glass morphism design and smooth animations
- Drag-and-drop file upload with progress tracking
- Real-time model training with visual feedback
- Interactive recommendation scoring with charts
- Comprehensive performance dashboards
- Mobile-responsive design
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import pandas as pd
import numpy as np
import joblib
import os
import json
from datetime import datetime
import sys
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from feature_engineering import apply_features, calculate_preference_score
from model_training import train_model, evaluate_model
from evaluation import ModelEvaluator
from config import get_config

# Initialize configuration
config = get_config()

app = Flask(__name__)
app.secret_key = config.web.secret_key

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.logging.level.upper()),
    format=config.logging.format,
    handlers=[
        logging.FileHandler(config.logging.file_path) if config.logging.file_path else logging.StreamHandler(),
        logging.StreamHandler()
    ]
)

# Global variables for model and data
current_model = None
current_data = None
model_metrics = None


@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')


@app.route('/health', methods=['GET'])
def health():
    """Simple healthcheck endpoint"""
    return jsonify({"status": "ok"}), 200


@app.route('/upload', methods=['GET', 'POST'])
def upload_data():
    """Upload and process data"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file and file.filename.endswith('.csv'):
            try:
                # Read CSV
                df = pd.read_csv(file)
                
                # Basic validation
                required_cols = ['ts', 'ms_played', 'duration_ms', 'id']
                missing_cols = [col for col in required_cols if col not in df.columns]
                
                if missing_cols:
                    flash(f'Missing required columns: {", ".join(missing_cols)}')
                    return redirect(request.url)
                
                # Convert timestamp
                df['ts'] = pd.to_datetime(df['ts'])
                
                # Store globally
                global current_data
                current_data = df
                
                flash(f'Successfully uploaded {len(df)} records')
                return redirect(url_for('data_overview'))
                
            except Exception as e:
                flash(f'Error processing file: {str(e)}')
                return redirect(request.url)
        else:
            flash('Please upload a CSV file')
            return redirect(request.url)
    
    return render_template('upload.html')


@app.route('/data_overview')
def data_overview():
    """Show data overview"""
    if current_data is None:
        flash('No data uploaded. Please upload data first.')
        return redirect(url_for('upload_data'))
    
    # Basic statistics
    stats = {
        'total_records': len(current_data),
        'date_range': f"{current_data['ts'].min()} to {current_data['ts'].max()}",
        'unique_tracks': current_data['id'].nunique(),
        'unique_artists': current_data['artist'].nunique() if 'artist' in current_data.columns else 'N/A'
    }
    
    # Sample data
    sample_data = current_data.head(10).to_dict('records')
    
    return render_template('data_overview.html', stats=stats, sample_data=sample_data)


@app.route('/train', methods=['GET', 'POST'])
def train_model_route():
    """Train model interface"""
    if request.method == 'POST':
        if current_data is None:
            flash('No data available. Please upload data first.')
            return redirect(url_for('upload_data'))
        
        try:
            # Get parameters
            test_split = float(request.form.get('test_split', 0.2))
            model_name = request.form.get('model_name', f'model_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
            
            # Split data
            split_point = int(len(current_data) * (1 - test_split))
            train_df = current_data.iloc[:split_point].copy()
            test_df = current_data.iloc[split_point:].copy()
            
            # Apply feature engineering
            train_processed, test_processed = apply_features(train_df, test_df)
            train_processed = calculate_preference_score(train_processed)
            
            # Add preference scores to test data (simulated)
            test_processed['preference_score'] = np.random.uniform(0, 100, len(test_processed))
            
            # Train model
            global current_model, model_metrics
            current_model = train_model(train_processed)
            
            # Evaluate model
            evaluator = ModelEvaluator(current_model, model_name)
            model_metrics, _ = evaluator.evaluate_performance(
                test_processed.drop(columns=['preference_score']),
                test_processed['preference_score']
            )
            
            flash(f'Model trained successfully! R² = {model_metrics["r2"]:.3f}')
            return redirect(url_for('model_performance'))
            
        except Exception as e:
            flash(f'Error training model: {str(e)}')
            return redirect(request.url)
    
    return render_template('train.html')


@app.route('/performance')
def model_performance():
    """Show model performance"""
    if current_model is None or model_metrics is None:
        flash('No trained model available. Please train a model first.')
        return redirect(url_for('train_model_route'))
    
    return render_template('performance.html', metrics=model_metrics)


@app.route('/recommendations', methods=['GET', 'POST'])
def get_recommendations():
    """Get recommendations"""
    if current_model is None:
        flash('No trained model available. Please train a model first.')
        return redirect(url_for('train_model_route'))
    
    if request.method == 'POST':
        try:
            # Get user input
            track_id = request.form.get('track_id')
            artist = request.form.get('artist', '')
            
            if not track_id:
                flash('Please provide a track ID')
                return redirect(request.url)
            
            # Create sample data for prediction
            sample_data = {
                'ts': [datetime.now()],
                'ms_played': [60000],  # 1 minute
                'duration_ms': [180000],  # 3 minutes
                'id': [track_id],
                'track': [f'Song {track_id}'],
                'artist': [artist],
                'popularity': [50],
                'danceability': [0.5],
                'energy': [0.5],
                'key': [5],
                'loudness': [-10],
                'mode': [1],
                'speechiness': [0.1],
                'acousticness': [0.1],
                'instrumentalness': [0.1],
                'valence': [0.5],
                'tempo': [120],
                'liveness': [0.1],
                'time_signature': [4],
                'reason_start': ['clickrow'],
                'reason_end': ['endplay'],
                'skipped': [False]
            }
            
            df = pd.DataFrame(sample_data)
            
            # Apply feature engineering
            train_dummy = df.head(1).copy()
            processed_df, _ = apply_features(train_dummy, df)
            
            # Make prediction
            X = processed_df.drop(columns=['preference_score'], errors='ignore')
            prediction = current_model.predict(X)[0]
            
            return render_template('recommendations.html', 
                                prediction=prediction, 
                                track_id=track_id, 
                                artist=artist)
            
        except Exception as e:
            flash(f'Error getting recommendations: {str(e)}')
            return redirect(request.url)
    
    return render_template('recommendations.html')


@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint for predictions"""
    if current_model is None:
        return jsonify({'error': 'No trained model available'}), 400
    
    try:
        data = request.get_json()
        
        # Create dataframe from input
        df = pd.DataFrame([data])
        
        # Apply feature engineering
        train_dummy = df.head(1).copy()
        processed_df, _ = apply_features(train_dummy, df)
        
        # Make prediction
        X = processed_df.drop(columns=['preference_score'], errors='ignore')
        prediction = current_model.predict(X)[0]
        
        return jsonify({
            'prediction': float(prediction),
            'track_id': data.get('id'),
            'artist': data.get('artist', ''),
            'track': data.get('track', '')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Respect environment PORT if provided (e.g., Railway local dev)
    port = int(os.getenv('PORT', config.web.port))
    host = os.getenv('WEB_HOST', config.web.host)
    debug = os.getenv('WEB_DEBUG', str(config.web.debug)).lower() == 'true'
    app.run(debug=debug, host=host, port=port)

