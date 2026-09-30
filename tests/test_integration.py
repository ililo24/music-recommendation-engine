import pytest
import sys
import os
import numpy as np

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from musicrec.ml.features import apply_features, calculate_preference_score
from musicrec.ml.training import train_model, evaluate_model


class TestIntegration:
    """Integration tests for the complete pipeline"""

    def create_sample_data(self, n_samples=100):
        """Create realistic sample data for integration testing"""
        import pandas as pd
        import numpy as np

        np.random.seed(42)

        data = {
            'ts': pd.date_range('2024-01-01', periods=n_samples, freq='H'),
            'ms_played': np.random.randint(10000, 300000, n_samples),
            'duration_ms': np.random.randint(60000, 300000, n_samples),
            'id': [f'track_{i%20}' for i in range(n_samples)],
            'track': [f'Song {i}' for i in range(n_samples)],
            'artist': [f'Artist {i%10}' for i in range(n_samples)],
            'popularity': np.random.randint(0, 100, n_samples),
            'danceability': np.random.random(n_samples),
            'energy': np.random.random(n_samples),
            'key': np.random.randint(0, 11, n_samples),
            'loudness': np.random.uniform(-20, 0, n_samples),
            'mode': np.random.randint(0, 2, n_samples),
            'speechiness': np.random.random(n_samples),
            'acousticness': np.random.random(n_samples),
            'instrumentalness': np.random.random(n_samples),
            'valence': np.random.random(n_samples),
            'tempo': np.random.uniform(60, 200, n_samples),
            'liveness': np.random.random(n_samples),
            'time_signature': np.random.randint(3, 8, n_samples),
            'reason_start': np.random.choice(['clickrow', 'fwdbtn', 'trackdone'], n_samples),
            'reason_end': np.random.choice(['backbtn', 'endplay', 'clickrow'], n_samples),
            'skipped': np.random.choice([True, False], n_samples)
        }

        return pd.DataFrame(data)

    def test_full_pipeline(self):
        """Test the complete pipeline from raw data to predictions"""
        # Create sample data
        raw_data = self.create_sample_data(200)

        # Split data
        split_point = int(len(raw_data) * 0.8)
        train_data = raw_data.iloc[:split_point].copy()
        test_data = raw_data.iloc[split_point:].copy()

        # Apply feature engineering
        train_processed, test_processed = apply_features(train_data, test_data)

        # Calculate preference scores for training data
        train_processed = calculate_preference_score(train_processed)

        # Add preference scores to test data (simulated)
        test_processed['preference_score'] = np.random.uniform(0, 100, len(test_processed))

        # Train model
        model = train_model(train_processed)

        # Evaluate model
        metrics = evaluate_model(model, test_processed)

        # Check that pipeline completed successfully
        assert model is not None
        assert 'mse' in metrics
        assert 'mae' in metrics
        assert 'r2' in metrics

        # Check that metrics are reasonable
        assert metrics['mse'] >= 0
        assert metrics['mae'] >= 0
        assert -1 <= metrics['r2'] <= 1

    def test_pipeline_with_missing_data(self):
        """Test pipeline robustness with missing data"""
        raw_data = self.create_sample_data(100)

        # Introduce some missing values
        raw_data.loc[10:15, 'danceability'] = np.nan
        raw_data.loc[20:25, 'energy'] = np.nan

        # Split data
        split_point = int(len(raw_data) * 0.8)
        train_data = raw_data.iloc[:split_point].copy()
        test_data = raw_data.iloc[split_point:].copy()

        # Apply feature engineering
        train_processed, test_processed = apply_features(train_data, test_data)

        # Calculate preference scores
        train_processed = calculate_preference_score(train_processed)
        test_processed['preference_score'] = np.random.uniform(0, 100, len(test_processed))

        # Should handle missing data gracefully
        model = train_model(train_processed)
        metrics = evaluate_model(model, test_processed)

        assert model is not None
        assert 'mse' in metrics

    def test_pipeline_performance(self):
        """Test that pipeline performs within reasonable time"""
        import time

        raw_data = self.create_sample_data(1000)

        # Split data
        split_point = int(len(raw_data) * 0.8)
        train_data = raw_data.iloc[:split_point].copy()
        test_data = raw_data.iloc[split_point:].copy()

        start_time = time.time()

        # Apply feature engineering
        train_processed, test_processed = apply_features(train_data, test_data)

        # Calculate preference scores
        train_processed = calculate_preference_score(train_processed)
        test_processed['preference_score'] = np.random.uniform(0, 100, len(test_processed))

        # Train model
        model = train_model(train_processed)
        metrics = evaluate_model(model, test_processed)

        end_time = time.time()
        execution_time = end_time - start_time

        # Pipeline should complete within reasonable time (adjust threshold as needed)
        assert execution_time < 30  # 30 seconds for 1000 samples


if __name__ == "__main__":
    pytest.main([__file__])
