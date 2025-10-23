# Models Directory

This directory stores trained models and their metadata.

## Files

- `recommendation_model_YYYYMMDD_HHMMSS.pkl` - Trained model files
- `model_metadata.json` - Model performance and configuration info

## Model Versions

Models are automatically versioned with timestamps. Each model includes:
- Trained pipeline (preprocessing + RandomForest)
- Performance metrics (MSE, MAE, R²)
- Feature importance scores
- Training configuration

## Usage

```python
import joblib
model = joblib.load('models/recommendation_model_20241023_130000.pkl')
predictions = model.predict(X_test)
```

