
# 🎵 Music Recommendation Engine

A sophisticated machine learning pipeline that predicts user music preferences based on listening behavior, completion rates, and audio features. Now with a complete web interface, comprehensive testing, and production-ready features!

## 🚀 Features

- **Real-time preference scoring** using completion rates and stream counts
- **Advanced feature engineering** with temporal and engagement features
- **Rewind behavior analysis** for high-engagement detection
- **Time-series aware** train/test splitting
- **Production-ready** ML pipeline with preprocessing
- **🌐 Web Interface** - Upload data, train models, get recommendations
- **🧪 Comprehensive Testing** - Unit tests, integration tests, coverage reports
- **📊 Model Evaluation** - Detailed performance analysis and visualization
- **⚙️ Configuration Management** - Environment-based config with validation
- **📈 Data Visualization** - Interactive charts and insights

## 📊 Model Performance

- **Cross-validation R²**: 0.85+
- **Mean Absolute Error**: <5.0
- **Feature Importance**: Completion rate, streams, time patterns

## 🛠️ Tech Stack

- **Python**: pandas, numpy, scikit-learn
- **ML**: Random Forest, Feature Engineering
- **Web**: Flask, Bootstrap, HTML/CSS/JS
- **Testing**: pytest, coverage analysis
- **Data**: Time-series analysis, Audio features
- **Visualization**: matplotlib, seaborn

## 📈 Key Insights

- **Rewind behavior** is a strong positive signal for music preference
- **Time-based patterns** significantly improve recommendation accuracy
- **Completion rate** is more predictive than raw play counts

## 🎯 Completed Features ✅

- [x] **Web application interface** - Complete Flask-based web app
- [x] **Comprehensive testing suite** - Unit, integration, and coverage tests
- [x] **Model evaluation tools** - Performance analysis and visualization
- [x] **Configuration management** - Environment-based settings
- [x] **Data visualization** - Interactive charts and insights
- [x] **CLI training script** - Command-line interface for model training
- [x] **Production-ready structure** - Organized, documented, and maintainable

## 🎯 Future Roadmap

- [ ] Spotify API integration
- [ ] Real-time recommendation engine
- [ ] NLP mood recognition
- [ ] Collaborative filtering
- [ ] Docker containerization
- [ ] API endpoints for mobile apps

## 📁 Project Structure
```
├── data/                    # Raw and processed data
│   ├── raw/                # Original data files
│   └── processed/          # Feature-engineered datasets
├── models/                  # Trained models and metadata
├── notebooks/               # Jupyter notebooks for analysis
├── src/                    # Source code
│   ├── feature_engineering.py  # Feature creation functions
│   ├── model_training.py      # Model training pipeline
│   ├── evaluation.py          # Model evaluation tools
│   ├── visualization.py       # Data visualization utilities
│   └── config.py             # Configuration management
├── tests/                  # Comprehensive test suite
│   ├── test_feature_engineering.py
│   ├── test_model_training.py
│   └── test_integration.py
├── templates/              # Web interface templates
├── static/                 # Web assets (CSS, JS)
├── logs/                   # Application logs
├── train.py               # CLI training script
├── web_app.py             # Flask web application
├── run_tests.py           # Test runner
└── setup.py               # Project setup script
```


## 🚀 Getting Started

### Quick Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/ililo24/music-recommendation-engine.git
cd music-recommendation-engine

# Run automated setup
python setup.py

# Start the web interface
python web_app.py
```

Visit `http://localhost:5000` to use the web interface!

### Manual Setup

#### Prerequisites
- Python 3.8+
- pip

#### Installation

```bash
# Clone the repository
git clone https://github.com/ililo24/music-recommendation-engine.git
cd music-recommendation-engine

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p data/{raw,processed} models notebooks logs

# Run tests
python run_tests.py
```

### Usage Options

#### 1. Web Interface (Easiest)
```bash
python web_app.py
```
- Upload your CSV data
- Train models with a few clicks
- Get recommendations instantly
- View performance metrics

#### 2. Command Line Interface
```bash
# Train a model
python train.py --data data/raw/listening_history.csv

# Train with custom parameters
python train.py --data data/raw/listening_history.csv --test-split 0.2 --model-name my_model

# Make predictions
python train.py --predict --model models/recommendation_model_20241023.pkl --data data/raw/new_data.csv
```

#### 3. Python API
```python
from src.feature_engineering import apply_features, calculate_preference_score
from src.model_training import train_model, evaluate_model
from src.evaluation import ModelEvaluator
from src.visualization import DataVisualizer

# Load your data
df = pd.read_csv('data/raw/your_data.csv')

# Apply feature engineering
train_processed, test_processed = apply_features(train_df, test_df)

# Calculate preference scores
train_processed = calculate_preference_score(train_processed)

# Train model
model = train_model(train_processed)

# Evaluate model
evaluator = ModelEvaluator(model)
metrics = evaluator.evaluate_performance(X_test, y_test)

# Visualize data
visualizer = DataVisualizer(df)
visualizer.plot_listening_patterns()
```

## 📊 Results

The model achieves high accuracy in predicting user preferences by leveraging:
- **Completion rates** as primary engagement signals
- **Rewind behavior** for high-engagement detection
- **Temporal patterns** for context-aware recommendations

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python run_tests.py

# Run with coverage
python run_tests.py --coverage

# Run specific test types
python run_tests.py --unit
python run_tests.py --integration
```

## 📈 Data Visualization

Explore your data with built-in visualization tools:

```python
from src.visualization import DataVisualizer

# Create visualizer
visualizer = DataVisualizer(df)

# Generate comprehensive visualizations
visualizer.plot_listening_patterns()
visualizer.plot_audio_features()
visualizer.plot_engagement_analysis()
visualizer.plot_correlation_matrix()
visualizer.plot_preference_analysis()

# Generate data report
visualizer.generate_data_report('data_report.json')
```

## ⚙️ Configuration

Customize the system with environment variables or config files:

```bash
# Environment variables
export MODEL_N_ESTIMATORS=300
export TEST_SPLIT=0.25
export LOG_LEVEL=DEBUG

# Or edit config.json
python -c "from src.config import create_sample_config; create_sample_config()"
```

## 🌐 Web Interface Features

- **📤 Data Upload**: Drag-and-drop CSV upload with validation
- **🤖 Model Training**: One-click model training with progress tracking
- **📊 Performance Dashboard**: Real-time metrics and visualizations
- **🔮 Recommendations**: Instant preference scoring for any track
- **📈 Analytics**: Comprehensive data exploration tools

## 🤝 Contributing

Open to contributions! This project aims to create better music recommendation algorithms.

### Development Setup
```bash
# Clone and setup for development
git clone https://github.com/ililo24/music-recommendation-engine.git
cd music-recommendation-engine
python setup.py --dev

# Run code quality checks
black .
flake8 .
python run_tests.py --coverage
```

## 📄 License

MIT License - feel free to use for learning and projects.

## 👨‍💻 Author

**Ililo Altaye** - [GitHub](https://github.com/ililo24)

---

⭐ **Star this repo if you found it helpful**
