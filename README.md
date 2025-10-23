
# 🎵 Music Recommendation Engine

A sophisticated machine learning pipeline that predicts user music preferences based on listening behavior, completion rates, and audio features.

## 🚀 Features

- **Real-time preference scoring** using completion rates and stream counts
- **Advanced feature engineering** with temporal and engagement features
- **Rewind behavior analysis** for high-engagement detection
- **Time-series aware** train/test splitting
- **Production-ready** ML pipeline with preprocessing

## 📊 Model Performance

- **Cross-validation R²**: 0.85+
- **Mean Absolute Error**: <5.0
- **Feature Importance**: Completion rate, streams, time patterns

## 🛠️ Tech Stack

- **Python**: pandas, numpy, scikit-learn
- **ML**: Random Forest, Feature Engineering
- **Data**: Time-series analysis, Audio features

## 📈 Key Insights

- **Rewind behavior** is a strong positive signal for music preference
- **Time-based patterns** significantly improve recommendation accuracy
- **Completion rate** is more predictive than raw play counts

## 🎯 Future Roadmap

- [ ] Web application interface
- [ ] Spotify API integration
- [ ] Real-time recommendation engine
- [ ] NLP mood recognition
- [ ] Collaborative filtering

## 📁 Project Structure
├── data/ # Raw and processed data
├── models/ # Trained models and metadata
├── notebooks/ # Jupyter notebooks
├── src/ # Source code
└── tests/ # Unit tests


## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/music-recommendation-engine.git
cd music-recommendation-engine

# Install dependencies
pip install -r requirements.txt

# Run the notebook
jupyter notebook notebooks/music_recommendation.ipynb
```

### Usage
```python
from src.feature_engineering import apply_features
from src.model_training import train_model

# Load your data
df = pd.read_csv('data/your_data.csv')

# Apply feature engineering
df_processed = apply_features(df)

# Train model
model = train_model(df_processed)
```

## 📊 Results

The model achieves high accuracy in predicting user preferences by leveraging:
- **Completion rates** as primary engagement signals
- **Rewind behavior** for high-engagement detection
- **Temporal patterns** for context-aware recommendations

## 🤝 Contributing

Open to contributions! This project aims to create better music recommendation algorithms.

## 📄 License

MIT License - feel free to use for learning and projects.

## 👨‍💻 Author

**Ililo Altaye** - [GitHub](https://github.com/ililo24)

--
⭐ **Star this repo if you found it helpful*
