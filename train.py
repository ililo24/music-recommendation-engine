#!/usr/bin/env python3
"""
Main training script for the music recommendation engine.

This script provides a command-line interface for training models,
evaluating performance, and making predictions.

Usage:
    python train.py --data data/raw/listening_history.csv
    python train.py --data data/raw/listening_history.csv --test-split 0.2
    python train.py --data data/raw/listening_history.csv --model-name my_model
    python train.py --predict --model models/recommendation_model_20241023.pkl --data data/raw/new_data.csv
"""

import argparse
import pandas as pd
import numpy as np
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from feature_engineering import apply_features, calculate_preference_score
from model_training import train_model, evaluate_model


def load_data(file_path):
    """Load data from CSV file"""
    try:
        df = pd.read_csv(file_path)
        print(f"✅ Loaded data: {len(df)} rows, {len(df.columns)} columns")
        
        # Convert timestamp column if it exists
        if 'ts' in df.columns:
            df['ts'] = pd.to_datetime(df['ts'])
            print(f"📅 Date range: {df['ts'].min()} to {df['ts'].max()}")
        
        return df
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        sys.exit(1)


def split_data(df, test_split=0.2, time_based=True):
    """Split data into train/test sets"""
    if time_based and 'ts' in df.columns:
        # Time-based split (recommended for time series)
        df_sorted = df.sort_values('ts')
        split_point = int(len(df_sorted) * (1 - test_split))
        train_df = df_sorted.iloc[:split_point].copy()
        test_df = df_sorted.iloc[split_point:].copy()
        print(f"📊 Time-based split: {len(train_df)} train, {len(test_df)} test")
    else:
        # Random split
        train_df = df.sample(frac=1-test_split, random_state=42)
        test_df = df.drop(train_df.index)
        print(f"📊 Random split: {len(train_df)} train, {len(test_df)} test")
    
    return train_df, test_df


def train_pipeline(train_df, test_df, model_name=None):
    """Train the complete pipeline"""
    print("🔧 Applying feature engineering...")
    
    # Apply feature engineering
    train_processed, test_processed = apply_features(train_df, test_df)
    
    # Calculate preference scores for training data
    train_processed = calculate_preference_score(train_processed)
    
    # Add preference scores to test data (simulated for evaluation)
    test_processed['preference_score'] = np.random.uniform(0, 100, len(test_processed))
    
    print(f"✅ Feature engineering complete: {len(train_processed.columns)} features")
    
    # Train model
    print("🤖 Training model...")
    model = train_model(train_processed)
    
    # Evaluate model
    print("📊 Evaluating model...")
    metrics = evaluate_model(model, test_processed)
    
    # Save model metadata
    if model_name:
        metadata = {
            'model_name': model_name,
            'training_date': datetime.now().isoformat(),
            'train_samples': len(train_processed),
            'test_samples': len(test_processed),
            'features': list(train_processed.columns),
            'metrics': metrics,
            'model_type': 'RandomForestRegressor'
        }
        
        metadata_path = f"models/{model_name}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"💾 Model metadata saved to {metadata_path}")
    
    return model, metrics


def predict(model_path, data_path, output_path=None):
    """Make predictions using a trained model"""
    import joblib
    
    # Load model
    print(f"📂 Loading model from {model_path}")
    model = joblib.load(model_path)
    
    # Load data
    df = load_data(data_path)
    
    # Apply feature engineering (without preference scores)
    print("🔧 Applying feature engineering...")
    train_dummy = df.head(1).copy()  # Dummy for reference stats
    processed_df, _ = apply_features(train_dummy, df)
    
    # Make predictions
    print("🔮 Making predictions...")
    X = processed_df.drop(columns=['preference_score'], errors='ignore')
    predictions = model.predict(X)
    
    # Add predictions to dataframe
    df['predicted_preference_score'] = predictions
    
    # Save results
    if output_path:
        df.to_csv(output_path, index=False)
        print(f"💾 Predictions saved to {output_path}")
    else:
        print("📊 Prediction results:")
        print(df[['track', 'artist', 'predicted_preference_score']].head(10))
    
    return df


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Music Recommendation Engine Training')
    
    # Data arguments
    parser.add_argument('--data', required=True, help='Path to training data CSV')
    parser.add_argument('--test-split', type=float, default=0.2, help='Test split ratio (default: 0.2)')
    
    # Model arguments
    parser.add_argument('--model-name', help='Custom model name')
    parser.add_argument('--predict', action='store_true', help='Make predictions instead of training')
    parser.add_argument('--model', help='Path to model file for predictions')
    parser.add_argument('--output', help='Output file for predictions')
    
    # Other arguments
    parser.add_argument('--random-split', action='store_true', help='Use random split instead of time-based')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Create necessary directories
    os.makedirs('models', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    if args.predict:
        # Prediction mode
        if not args.model:
            print("❌ --model required for prediction mode")
            sys.exit(1)
        
        predict(args.model, args.data, args.output)
    
    else:
        # Training mode
        # Load data
        df = load_data(args.data)
        
        # Split data
        train_df, test_df = split_data(df, args.test_split, not args.random_split)
        
        # Train pipeline
        model, metrics = train_pipeline(train_df, test_df, args.model_name)
        
        print("\n🎉 Training complete!")
        print(f"📊 Final metrics: R²={metrics['r2']:.3f}, MAE={metrics['mae']:.3f}")


if __name__ == '__main__':
    main()
