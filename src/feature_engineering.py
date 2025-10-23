import pandas as pd
import numpy as np

def create_time_features(df):
    """Create time-based features from timestamp"""
    df = df.copy()
    
    df['hour'] = df['ts'].dt.hour
    df['day_of_week'] = df['ts'].dt.dayofweek
    df['month'] = df['ts'].dt.month
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(bool)
    
    df['time_of_day'] = pd.cut(df['hour'], 
                            bins=[0, 4, 12, 17, 24],
                            labels=['Mid-Night', 'Morning', 'Afternoon', 'Night'],
                            include_lowest=True)
    return df

def create_completion_features(df):
    """Create completion-based features"""
    df = df.copy()
    df['rewound'] = (df['ms_played'] > df['duration_ms']).astype(bool)
    df['completion_rate'] = (df['ms_played']/df['duration_ms'])*100
    return df

def create_categorical_features(df):
    """Create categorical features"""
    df = df.copy()
    mapping = {
        'clickrow': 'new',
        'fwdbtn': 'user',
        'trackdone': 'natural',
        'backbtn': 'user',
        'endplay': 'natural'  # Fixed the typo
    }
    
    df['reason_start'] = df['reason_start'].map(mapping)
    df['reason_end'] = df['reason_end'].map(mapping)
    return df

def create_engagement_features(df, reference_stats=None):
    """Create engagement features"""
    df = df.copy()
    
    if reference_stats is None:
        track_stats = df.groupby('id').agg(
            avg_completion_rate=('completion_rate', 'mean'),
            streams=('id', 'count')
        ).reset_index()
    else:
        track_stats = reference_stats  # Fixed the bug
    
    df = pd.merge(df, track_stats, on='id', how='left')
    return df, track_stats

def calculate_preference_score(df, weights=(0.6, 0.7)):
    """Calculate preference score"""
    df = df.copy()
    
    df['streams'] = df.groupby('id')['id'].transform('count')
    df['norm_completion'] = df['avg_completion_rate'] / 100
    df['norm_streams'] = np.log1p(df['streams']) / np.log1p(df['streams'].max())
    
    df['preference_score'] = (
        weights[0] * df['norm_completion'] +
        weights[1] * df['norm_streams']
    ) * 100
    
    df['preference_score'] = df['preference_score'].clip(0, 100)
    return df

def apply_features(train_df, test_df=None):
    """Apply all feature engineering"""
    # Process training data
    train_df = create_time_features(train_df)
    train_df = create_categorical_features(train_df)
    train_df = create_completion_features(train_df)
    train_df, track_stats = create_engagement_features(train_df, reference_stats=None)
    
    # Process test data if provided
    if test_df is not None:
        test_df = create_time_features(test_df)
        test_df = create_categorical_features(test_df)
        test_df = create_completion_features(test_df)
        test_df, _ = create_engagement_features(test_df, reference_stats=track_stats)
        
        test_df = test_df.drop(['avg_completion_rate', 'streams'], axis=1, errors='ignore')
        test_df = pd.merge(test_df, track_stats, on='id', how='left', suffixes=('', '_stat'))
        
        global_avg = train_df['completion_rate'].mean()
        test_df['completion_rate'] = test_df['completion_rate'].fillna(global_avg)
        test_df['streams'] = test_df['streams'].fillna(0)
    
    return train_df, test_df
