import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from feature_engineering import (
    create_time_features,
    create_completion_features,
    create_categorical_features,
    create_engagement_features,
    calculate_preference_score,
    apply_features
)


class TestTimeFeatures:
    """Test time-based feature creation"""
    
    def test_create_time_features_basic(self):
        """Test basic time feature creation"""
        # Create test data
        timestamps = pd.date_range('2024-01-01', periods=10, freq='H')
        df = pd.DataFrame({'ts': timestamps})
        
        result = create_time_features(df)
        
        # Check that time features are created
        assert 'hour' in result.columns
        assert 'day_of_week' in result.columns
        assert 'month' in result.columns
        assert 'is_weekend' in result.columns
        assert 'time_of_day' in result.columns
        
        # Check data types
        assert result['hour'].dtype == 'int64'
        assert result['is_weekend'].dtype == 'bool'
        
    def test_weekend_detection(self):
        """Test weekend detection logic"""
        # Create data with known weekends
        timestamps = pd.to_datetime(['2024-01-06', '2024-01-07', '2024-01-08'])  # Sat, Sun, Mon
        df = pd.DataFrame({'ts': timestamps})
        
        result = create_time_features(df)
        
        # Saturday and Sunday should be weekend
        assert result.iloc[0]['is_weekend'] == True
        assert result.iloc[1]['is_weekend'] == True
        assert result.iloc[2]['is_weekend'] == False
        
    def test_time_of_day_categorization(self):
        """Test time of day categorization"""
        timestamps = pd.to_datetime([
            '2024-01-01 02:00',  # Mid-Night
            '2024-01-01 08:00',  # Morning
            '2024-01-01 14:00',  # Afternoon
            '2024-01-01 20:00'   # Night
        ])
        df = pd.DataFrame({'ts': timestamps})
        
        result = create_time_features(df)
        
        expected_categories = ['Mid-Night', 'Morning', 'Afternoon', 'Night']
        assert all(cat in expected_categories for cat in result['time_of_day'].cat.categories)


class TestCompletionFeatures:
    """Test completion-based feature creation"""
    
    def test_create_completion_features_basic(self):
        """Test basic completion feature creation"""
        df = pd.DataFrame({
            'ms_played': [30000, 60000, 120000],
            'duration_ms': [60000, 60000, 60000]
        })
        
        result = create_completion_features(df)
        
        assert 'rewound' in result.columns
        assert 'completion_rate' in result.columns
        
        # Check completion rate calculation
        expected_completion = [50.0, 100.0, 200.0]
        assert np.allclose(result['completion_rate'], expected_completion)
        
        # Check rewind detection
        expected_rewound = [False, False, True]
        assert result['rewound'].tolist() == expected_rewound
        
    def test_completion_rate_edge_cases(self):
        """Test edge cases for completion rate"""
        df = pd.DataFrame({
            'ms_played': [0, 30000, 60000],
            'duration_ms': [60000, 0, 60000]  # Zero duration case
        })
        
        result = create_completion_features(df)
        
        # Zero duration should result in inf completion rate
        assert np.isinf(result.iloc[1]['completion_rate'])
        assert result.iloc[0]['completion_rate'] == 0.0
        assert result.iloc[2]['completion_rate'] == 100.0


class TestCategoricalFeatures:
    """Test categorical feature creation"""
    
    def test_create_categorical_features(self):
        """Test categorical feature mapping"""
        df = pd.DataFrame({
            'reason_start': ['clickrow', 'fwdbtn', 'trackdone'],
            'reason_end': ['backbtn', 'endplay', 'clickrow']
        })
        
        result = create_categorical_features(df)
        
        # Check that mapping is applied
        assert result['reason_start'].iloc[0] == 'new'
        assert result['reason_start'].iloc[1] == 'user'
        assert result['reason_start'].iloc[2] == 'natural'
        
        assert result['reason_end'].iloc[0] == 'user'
        assert result['reason_end'].iloc[1] == 'natural'
        assert result['reason_end'].iloc[2] == 'new'


class TestEngagementFeatures:
    """Test engagement feature creation"""
    
    def test_create_engagement_features_basic(self):
        """Test basic engagement feature creation"""
        df = pd.DataFrame({
            'id': ['track1', 'track1', 'track2', 'track2'],
            'completion_rate': [50, 80, 30, 90]
        })
        
        result, track_stats = create_engagement_features(df)
        
        # Check that engagement features are added
        assert 'avg_completion_rate' in result.columns
        assert 'streams' in result.columns
        
        # Check track statistics
        assert len(track_stats) == 2
        assert track_stats['avg_completion_rate'].iloc[0] == 65.0  # (50+80)/2
        assert track_stats['streams'].iloc[0] == 2
        
    def test_engagement_features_with_reference_stats(self):
        """Test engagement features with reference statistics"""
        df = pd.DataFrame({
            'id': ['track1', 'track2'],
            'completion_rate': [50, 80]
        })
        
        reference_stats = pd.DataFrame({
            'id': ['track1', 'track2'],
            'avg_completion_rate': [65.0, 75.0],
            'streams': [2, 1]
        })
        
        result, _ = create_engagement_features(df, reference_stats)
        
        # Should use reference stats instead of calculating new ones
        assert result['avg_completion_rate'].iloc[0] == 65.0
        assert result['streams'].iloc[0] == 2


class TestPreferenceScore:
    """Test preference score calculation"""
    
    def test_calculate_preference_score_basic(self):
        """Test basic preference score calculation"""
        df = pd.DataFrame({
            'id': ['track1', 'track1', 'track2'],
            'avg_completion_rate': [80, 80, 60],
            'streams': [2, 2, 1]
        })
        
        result = calculate_preference_score(df)
        
        assert 'preference_score' in result.columns
        assert 'norm_completion' in result.columns
        assert 'norm_streams' in result.columns
        
        # Check that scores are between 0 and 100
        assert result['preference_score'].min() >= 0
        assert result['preference_score'].max() <= 100
        
    def test_preference_score_weights(self):
        """Test preference score with custom weights"""
        df = pd.DataFrame({
            'id': ['track1'],
            'avg_completion_rate': [80],
            'streams': [1]
        })
        
        # Test with different weights
        result1 = calculate_preference_score(df, weights=(0.8, 0.2))
        result2 = calculate_preference_score(df, weights=(0.2, 0.8))
        
        # Scores should be different with different weights
        assert result1['preference_score'].iloc[0] != result2['preference_score'].iloc[0]


class TestApplyFeatures:
    """Test the main apply_features function"""
    
    def test_apply_features_train_only(self):
        """Test apply_features with training data only"""
        df = pd.DataFrame({
            'ts': pd.date_range('2024-01-01', periods=5, freq='H'),
            'ms_played': [30000] * 5,
            'duration_ms': [60000] * 5,
            'id': ['track1'] * 5,
            'reason_start': ['clickrow'] * 5,
            'reason_end': ['endplay'] * 5
        })
        
        result_train, result_test = apply_features(df)
        
        # Check that all features are created
        expected_features = ['hour', 'day_of_week', 'month', 'is_weekend', 'time_of_day',
                           'rewound', 'completion_rate', 'avg_completion_rate', 'streams']
        
        for feature in expected_features:
            assert feature in result_train.columns
            
        # Test data should be None
        assert result_test is None
        
    def test_apply_features_train_and_test(self):
        """Test apply_features with both training and test data"""
        train_df = pd.DataFrame({
            'ts': pd.date_range('2024-01-01', periods=3, freq='H'),
            'ms_played': [30000] * 3,
            'duration_ms': [60000] * 3,
            'id': ['track1'] * 3,
            'reason_start': ['clickrow'] * 3,
            'reason_end': ['endplay'] * 3
        })
        
        test_df = pd.DataFrame({
            'ts': pd.date_range('2024-01-02', periods=2, freq='H'),
            'ms_played': [30000] * 2,
            'duration_ms': [60000] * 2,
            'id': ['track1'] * 2,
            'reason_start': ['clickrow'] * 2,
            'reason_end': ['endplay'] * 2
        })
        
        result_train, result_test = apply_features(train_df, test_df)
        
        # Both should have the same features
        assert len(result_train.columns) == len(result_test.columns)
        
        # Test data should have reference stats applied
        assert 'avg_completion_rate' in result_test.columns
        assert 'streams' in result_test.columns


if __name__ == "__main__":
    pytest.main([__file__])
