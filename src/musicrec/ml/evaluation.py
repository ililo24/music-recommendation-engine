"""
Model evaluation and visualization utilities for the music recommendation engine.

This module provides comprehensive evaluation metrics, feature importance analysis,
and visualization tools for understanding model performance.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import cross_val_score


class ModelEvaluator:
    """Comprehensive model evaluation and analysis"""

    def __init__(self, model, model_name=None):
        """Initialize evaluator with a trained model"""
        self.model = model
        self.model_name = model_name or "unnamed_model"
        self.feature_names = None
        self.feature_importance = None

    def evaluate_performance(self, X_test, y_test, cv_folds=5):
        """Comprehensive model performance evaluation"""
        # Basic metrics
        y_pred = self.model.predict(X_test)

        metrics = {
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred),
            'mape': np.mean(np.abs((y_test - y_pred) / y_test)) * 100
        }

        # Cross-validation scores
        cv_scores = cross_val_score(self.model, X_test, y_test, cv=cv_folds, scoring='r2')
        metrics['cv_r2_mean'] = cv_scores.mean()
        metrics['cv_r2_std'] = cv_scores.std()

        return metrics, y_pred

    def analyze_feature_importance(self, feature_names=None):
        """Analyze and visualize feature importance"""
        if hasattr(self.model, 'feature_importances_'):
            # For tree-based models
            importance = self.model.feature_importances_
        elif hasattr(self.model.named_steps['regressor'], 'feature_importances_'):
            # For pipeline models
            importance = self.model.named_steps['regressor'].feature_importances_
        else:
            print("❌ Model does not support feature importance analysis")
            return None

        # Get feature names
        if feature_names is None:
            if hasattr(self.model, 'feature_names_in_'):
                feature_names = self.model.feature_names_in_
            else:
                feature_names = [f'feature_{i}' for i in range(len(importance))]

        # Create importance dataframe
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)

        self.feature_importance = importance_df
        return importance_df

    def plot_feature_importance(self, top_n=20, figsize=(10, 8)):
        """Plot feature importance"""
        if self.feature_importance is None:
            print("❌ Run analyze_feature_importance() first")
            return

        plt.figure(figsize=figsize)
        top_features = self.feature_importance.head(top_n)

        sns.barplot(data=top_features, x='importance', y='feature')
        plt.title(f'Top {top_n} Feature Importance - {self.model_name}')
        plt.xlabel('Importance')
        plt.tight_layout()
        plt.show()

        return top_features

    def plot_predictions_vs_actual(self, y_test, y_pred, figsize=(10, 6)):
        """Plot predictions vs actual values"""
        plt.figure(figsize=figsize)

        plt.scatter(y_test, y_pred, alpha=0.6)
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)

        plt.xlabel('Actual Preference Score')
        plt.ylabel('Predicted Preference Score')
        plt.title(f'Predictions vs Actual - {self.model_name}')

        # Add R² to plot
        r2 = r2_score(y_test, y_pred)
        plt.text(0.05, 0.95, f'R² = {r2:.3f}', transform=plt.gca().transAxes,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        plt.tight_layout()
        plt.show()

    def plot_residuals(self, y_test, y_pred, figsize=(12, 5)):
        """Plot residual analysis"""
        residuals = y_test - y_pred

        fig, axes = plt.subplots(1, 2, figsize=figsize)

        # Residuals vs predictions
        axes[0].scatter(y_pred, residuals, alpha=0.6)
        axes[0].axhline(y=0, color='r', linestyle='--')
        axes[0].set_xlabel('Predicted Values')
        axes[0].set_ylabel('Residuals')
        axes[0].set_title('Residuals vs Predictions')

        # Residuals histogram
        axes[1].hist(residuals, bins=30, alpha=0.7, edgecolor='black')
        axes[1].set_xlabel('Residuals')
        axes[1].set_ylabel('Frequency')
        axes[1].set_title('Residuals Distribution')

        plt.tight_layout()
        plt.show()

    def generate_report(self, X_test, y_test):
        """Generate comprehensive evaluation report"""
        print(f"📊 Model Evaluation Report: {self.model_name}")
        print("=" * 50)

        # Performance metrics
        metrics, y_pred = self.evaluate_performance(X_test, y_test)

        print("\n🎯 Performance Metrics:")
        print(f"   R² Score: {metrics['r2']:.4f}")
        print(f"   RMSE: {metrics['rmse']:.4f}")
        print(f"   MAE: {metrics['mae']:.4f}")
        print(f"   MAPE: {metrics['mape']:.2f}%")
        print(f"   CV R² (mean ± std): {metrics['cv_r2_mean']:.4f} ± {metrics['cv_r2_std']:.4f}")

        # Feature importance
        importance_df = self.analyze_feature_importance()
        if importance_df is not None:
            print(f"\n🔍 Top 10 Most Important Features:")
            for i, row in importance_df.head(10).iterrows():
                print(f"   {row['feature']}: {row['importance']:.4f}")

        # Error analysis
        residuals = y_test - y_pred
        print(f"\n📈 Error Analysis:")
        print(f"   Mean Residual: {residuals.mean():.4f}")
        print(f"   Residual Std: {residuals.std():.4f}")
        print(f"   Max Error: {residuals.abs().max():.4f}")

        return metrics, importance_df


def compare_models(models_dict, X_test, y_test):
    """Compare multiple models"""
    comparison_results = {}

    for name, model in models_dict.items():
        evaluator = ModelEvaluator(model, name)
        metrics, _ = evaluator.evaluate_performance(X_test, y_test)
        comparison_results[name] = metrics

    # Create comparison dataframe
    comparison_df = pd.DataFrame(comparison_results).T

    # Plot comparison
    plt.figure(figsize=(12, 8))

    metrics_to_plot = ['r2', 'rmse', 'mae']
    for i, metric in enumerate(metrics_to_plot):
        plt.subplot(2, 2, i+1)
        comparison_df[metric].plot(kind='bar')
        plt.title(f'{metric.upper()} Comparison')
        plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()

    return comparison_df


if __name__ == "__main__":
    # Example usage
    print("🔧 Model Evaluation Utilities")
    print("This module provides comprehensive model evaluation tools.")
    print("Use ModelEvaluator class to analyze your trained models.")
