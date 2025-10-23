import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
from datetime import datetime
import json

def train_model(train_df, test_df=None):
    """Train the music recommendation model"""
    
    # Define features
    target = 'preference_score'
    num_features = ['ms_played', 'popularity', 'duration_ms', 'danceability', 'energy', 
                   'key', 'loudness', 'mode', 'speechiness', 'acousticness', 
                   'instrumentalness', 'valence', 'tempo', 'liveness', 'time_signature', 
                   'hour', 'day_of_week', 'month', 'completion_rate', 'avg_completion_rate', 'streams']
    
    cat_features = ['reason_start', 'reason_end', 'skipped', 'is_weekend', 'time_of_day', 'rewound']
    
    # Create preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features)
        ]
    )
    
    # Create model pipeline
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=200, random_state=2, n_jobs=-1))
    ])
    
    # Train model
    X_train = train_df.drop(columns=[target])
    y_train = train_df[target]
    
    model.fit(X_train, y_train)
    
    # Save model
    model_version = datetime.now().strftime("%Y%m%d_%H%M%S")
    joblib.dump(model, f'models/recommendation_model_{model_version}.pkl')
    
    print(f"✅ Model trained and saved as version {model_version}")
    return model

def evaluate_model(model, test_df, target='preference_score'):
    """Evaluate model performance"""
    X_test = test_df.drop(columns=[target])
    y_test = test_df[target]
    
    predictions = model.predict(X_test)
    
    mse = mean_squared_error(y_test, predictions)
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    
    print(f"📊 Model Performance:")
    print(f"   MSE: {mse:.4f}")
    print(f"   MAE: {mae:.4f}")
    print(f"   R²: {r2:.4f}")
    
    return {'mse': mse, 'mae': mae, 'r2': r2}
