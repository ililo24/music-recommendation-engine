import pytest
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import MagicMock

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from musicrec.ml.training import train_model, evaluate_model


class TestModelTraining:
    """Test model training functionality"""

    def create_sample_data(self):
        """Create sample data for testing"""
        np.random.seed(42)
        n_samples = 100

        data = {
            'ts': pd.date_range('2024-01-01', periods=n_samples, freq='H'),
            'ms_played': np.random.randint(10000, 300000, n_samples),
            'duration_ms': np.random.randint(60000, 300000, n_samples),
            'id': [f'track_{i%10}' for i in range(n_samples)],
            'track': [f'Song {i}' for i in range(n_samples)],
            'artist': [f'Artist {i%5}' for i in range(n_samples)],
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
            'skipped': np.random.choice([True, False], n_samples),
            'hour': np.random.randint(0, 24, n_samples),
            'day_of_week': np.random.randint(0, 7, n_samples),
            'month': np.random.randint(1, 13, n_samples),
            'is_weekend': np.random.choice([True, False], n_samples),
            'time_of_day': np.random.choice(['Morning', 'Afternoon', 'Evening', 'Night'], n_samples),
            'rewound': np.random.choice([True, False], n_samples),
            'completion_rate': np.random.uniform(0, 200, n_samples),
            'avg_completion_rate': np.random.uniform(0, 100, n_samples),
            'streams': np.random.randint(1, 50, n_samples),
            'preference_score': np.random.uniform(0, 100, n_samples)
        }

        return pd.DataFrame(data)

    def test_train_model_basic(self):
        """Test basic model training"""
        train_df = self.create_sample_data()

        model = train_model(train_df)

        # Check that model is returned
        assert model is not None
        assert hasattr(model, 'fit')
        assert hasattr(model, 'predict')

    def test_train_model_with_test_data(self):
        """Test model training with test data"""
        train_df = self.create_sample_data()
        test_df = self.create_sample_data()

        model = train_model(train_df, test_df)

        # Model should still be trained on training data
        assert model is not None

    def test_train_model_feature_columns(self):
        """Test that model uses correct feature columns"""
        train_df = self.create_sample_data()

        model = train_model(train_df)

        # Check that target column is not in features
        X_train = train_df.drop(columns=['preference_score'])
        y_train = train_df['preference_score']

        # Model should be able to fit
        model.fit(X_train, y_train)

        # Should be able to predict
        predictions = model.predict(X_train.head(5))
        assert len(predictions) == 5

    def test_train_model_missing_features(self):
        """Test model training with missing features"""
        train_df = self.create_sample_data()

        # Remove some features
        train_df = train_df.drop(columns=['danceability', 'energy'])

        # Should handle missing features gracefully
        try:
            model = train_model(train_df)
            # If it doesn't fail, check that it still works
            assert model is not None
        except (KeyError, ValueError):
            # Expected behavior for missing required features
            pass


class TestModelEvaluation:
    """Test model evaluation functionality"""

    def create_sample_data(self):
        """Create sample data for testing"""
        np.random.seed(42)
        n_samples = 50

        data = {
            'ms_played': np.random.randint(10000, 300000, n_samples),
            'duration_ms': np.random.randint(60000, 300000, n_samples),
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
            'skipped': np.random.choice([True, False], n_samples),
            'hour': np.random.randint(0, 24, n_samples),
            'day_of_week': np.random.randint(0, 7, n_samples),
            'month': np.random.randint(1, 13, n_samples),
            'is_weekend': np.random.choice([True, False], n_samples),
            'time_of_day': np.random.choice(['Morning', 'Afternoon', 'Evening', 'Night'], n_samples),
            'rewound': np.random.choice([True, False], n_samples),
            'completion_rate': np.random.uniform(0, 200, n_samples),
            'avg_completion_rate': np.random.uniform(0, 100, n_samples),
            'streams': np.random.randint(1, 50, n_samples),
            'preference_score': np.random.uniform(0, 100, n_samples)
        }

        return pd.DataFrame(data)

    def test_evaluate_model_basic(self):
        """Test basic model evaluation"""
        test_df = self.create_sample_data()

        # Create a mock model
        mock_model = MagicMock()
        mock_model.predict.return_value = np.random.uniform(0, 100, len(test_df))

        metrics = evaluate_model(mock_model, test_df)

        # Check that metrics are returned
        assert 'mse' in metrics
        assert 'mae' in metrics
        assert 'r2' in metrics

        # Check that metrics are numeric
        assert isinstance(metrics['mse'], (int, float))
        assert isinstance(metrics['mae'], (int, float))
        assert isinstance(metrics['r2'], (int, float))

    def test_evaluate_model_perfect_predictions(self):
        """Test evaluation with perfect predictions"""
        test_df = self.create_sample_data()

        # Create a mock model that returns perfect predictions
        mock_model = MagicMock()
        mock_model.predict.return_value = test_df['preference_score'].values

        metrics = evaluate_model(mock_model, test_df)

        # Perfect predictions should give R² = 1.0
        assert metrics['r2'] == 1.0
        assert metrics['mse'] == 0.0
        assert metrics['mae'] == 0.0

    def test_evaluate_model_custom_target(self):
        """Test evaluation with custom target column"""
        test_df = self.create_sample_data()
        test_df['custom_target'] = test_df['preference_score'] + 10

        # Create a mock model
        mock_model = MagicMock()
        mock_model.predict.return_value = np.random.uniform(0, 100, len(test_df))

        metrics = evaluate_model(mock_model, test_df, target='custom_target')

        # Should work with custom target
        assert 'mse' in metrics
        assert 'mae' in metrics
        assert 'r2' in metrics


if __name__ == "__main__":
    pytest.main([__file__])
