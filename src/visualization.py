"""
Data visualization utilities for the music recommendation engine.

This module provides visualization tools for exploring data patterns,
model performance, and recommendation insights.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class DataVisualizer:
    """Comprehensive data visualization for music recommendation data"""
    
    def __init__(self, df):
        """Initialize with a dataframe"""
        self.df = df.copy()
        self.setup_plotting()
    
    def setup_plotting(self):
        """Setup plotting parameters"""
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        
    def plot_listening_patterns(self, figsize=(15, 10)):
        """Visualize listening patterns over time"""
        if 'ts' not in self.df.columns:
            print("❌ Timestamp column 'ts' not found")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        
        # Hourly patterns
        self.df['hour'] = self.df['ts'].dt.hour
        hourly_counts = self.df.groupby('hour').size()
        axes[0, 0].plot(hourly_counts.index, hourly_counts.values, marker='o')
        axes[0, 0].set_title('Listening Activity by Hour')
        axes[0, 0].set_xlabel('Hour of Day')
        axes[0, 0].set_ylabel('Number of Plays')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Daily patterns
        self.df['day_of_week'] = self.df['ts'].dt.day_name()
        daily_counts = self.df.groupby('day_of_week').size()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_counts = daily_counts.reindex(day_order)
        axes[0, 1].bar(range(len(daily_counts)), daily_counts.values)
        axes[0, 1].set_title('Listening Activity by Day of Week')
        axes[0, 1].set_xlabel('Day of Week')
        axes[0, 1].set_ylabel('Number of Plays')
        axes[0, 1].set_xticks(range(len(day_order)))
        axes[0, 1].set_xticklabels(day_order, rotation=45)
        
        # Completion rate distribution
        if 'completion_rate' in self.df.columns:
            axes[1, 0].hist(self.df['completion_rate'], bins=50, alpha=0.7, edgecolor='black')
            axes[1, 0].set_title('Completion Rate Distribution')
            axes[1, 0].set_xlabel('Completion Rate (%)')
            axes[1, 0].set_ylabel('Frequency')
            axes[1, 0].axvline(self.df['completion_rate'].mean(), color='red', linestyle='--', 
                              label=f'Mean: {self.df["completion_rate"].mean():.1f}%')
            axes[1, 0].legend()
        
        # Top artists
        if 'artist' in self.df.columns:
            top_artists = self.df['artist'].value_counts().head(10)
            axes[1, 1].barh(range(len(top_artists)), top_artists.values)
            axes[1, 1].set_title('Top 10 Artists by Play Count')
            axes[1, 1].set_xlabel('Number of Plays')
            axes[1, 1].set_yticks(range(len(top_artists)))
            axes[1, 1].set_yticklabels(top_artists.index)
        
        plt.tight_layout()
        plt.show()
    
    def plot_audio_features(self, figsize=(15, 10)):
        """Visualize audio feature distributions"""
        audio_features = ['danceability', 'energy', 'valence', 'acousticness', 
                         'instrumentalness', 'speechiness', 'liveness']
        
        available_features = [f for f in audio_features if f in self.df.columns]
        
        if not available_features:
            print("❌ No audio features found in data")
            return
        
        n_features = len(available_features)
        n_cols = 3
        n_rows = (n_features + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        axes = axes.flatten() if n_rows > 1 else [axes] if n_rows == 1 else axes
        
        for i, feature in enumerate(available_features):
            if i < len(axes):
                axes[i].hist(self.df[feature], bins=30, alpha=0.7, edgecolor='black')
                axes[i].set_title(f'{feature.title()} Distribution')
                axes[i].set_xlabel(feature.title())
                axes[i].set_ylabel('Frequency')
                axes[i].axvline(self.df[feature].mean(), color='red', linestyle='--',
                               label=f'Mean: {self.df[feature].mean():.3f}')
                axes[i].legend()
        
        # Hide empty subplots
        for i in range(len(available_features), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.show()
    
    def plot_engagement_analysis(self, figsize=(15, 8)):
        """Analyze user engagement patterns"""
        if 'completion_rate' not in self.df.columns:
            print("❌ Completion rate data not available")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        
        # Completion rate vs skip rate
        if 'skipped' in self.df.columns:
            skip_completion = self.df.groupby('skipped')['completion_rate'].mean()
            axes[0, 0].bar(['Not Skipped', 'Skipped'], skip_completion.values)
            axes[0, 0].set_title('Average Completion Rate by Skip Status')
            axes[0, 0].set_ylabel('Average Completion Rate (%)')
        
        # Rewind behavior
        if 'rewound' in self.df.columns:
            rewind_completion = self.df.groupby('rewound')['completion_rate'].mean()
            axes[0, 1].bar(['No Rewind', 'Rewound'], rewind_completion.values)
            axes[0, 1].set_title('Average Completion Rate by Rewind Status')
            axes[0, 1].set_ylabel('Average Completion Rate (%)')
        
        # Completion rate by time of day
        if 'time_of_day' in self.df.columns:
            time_completion = self.df.groupby('time_of_day')['completion_rate'].mean()
            axes[1, 0].bar(range(len(time_completion)), time_completion.values)
            axes[1, 0].set_title('Average Completion Rate by Time of Day')
            axes[1, 0].set_xlabel('Time of Day')
            axes[1, 0].set_ylabel('Average Completion Rate (%)')
            axes[1, 0].set_xticks(range(len(time_completion)))
            axes[1, 0].set_xticklabels(time_completion.index, rotation=45)
        
        # Completion rate distribution by weekend
        if 'is_weekend' in self.df.columns:
            weekend_data = [self.df[self.df['is_weekend'] == False]['completion_rate'],
                          self.df[self.df['is_weekend'] == True]['completion_rate']]
            axes[1, 1].hist(weekend_data, bins=30, alpha=0.7, 
                           label=['Weekday', 'Weekend'], edgecolor='black')
            axes[1, 1].set_title('Completion Rate Distribution by Weekend Status')
            axes[1, 1].set_xlabel('Completion Rate (%)')
            axes[1, 1].set_ylabel('Frequency')
            axes[1, 1].legend()
        
        plt.tight_layout()
        plt.show()
    
    def plot_correlation_matrix(self, figsize=(12, 10)):
        """Plot correlation matrix of numeric features"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            print("❌ Not enough numeric columns for correlation analysis")
            return
        
        # Calculate correlation matrix
        corr_matrix = self.df[numeric_cols].corr()
        
        # Create heatmap
        plt.figure(figsize=figsize)
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
        plt.title('Feature Correlation Matrix')
        plt.tight_layout()
        plt.show()
        
        return corr_matrix
    
    def plot_preference_analysis(self, figsize=(15, 10)):
        """Analyze preference score patterns"""
        if 'preference_score' not in self.df.columns:
            print("❌ Preference score not found in data")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        
        # Preference score distribution
        axes[0, 0].hist(self.df['preference_score'], bins=50, alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('Preference Score Distribution')
        axes[0, 0].set_xlabel('Preference Score')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].axvline(self.df['preference_score'].mean(), color='red', linestyle='--',
                          label=f'Mean: {self.df["preference_score"].mean():.1f}')
        axes[0, 0].legend()
        
        # Preference vs completion rate
        if 'completion_rate' in self.df.columns:
            axes[0, 1].scatter(self.df['completion_rate'], self.df['preference_score'], alpha=0.6)
            axes[0, 1].set_title('Preference Score vs Completion Rate')
            axes[0, 1].set_xlabel('Completion Rate (%)')
            axes[0, 1].set_ylabel('Preference Score')
            
            # Add trend line
            z = np.polyfit(self.df['completion_rate'], self.df['preference_score'], 1)
            p = np.poly1d(z)
            axes[0, 1].plot(self.df['completion_rate'], p(self.df['completion_rate']), "r--", alpha=0.8)
        
        # Top tracks by preference
        if 'track' in self.df.columns:
            top_tracks = self.df.groupby('track')['preference_score'].mean().sort_values(ascending=False).head(10)
            axes[1, 0].barh(range(len(top_tracks)), top_tracks.values)
            axes[1, 0].set_title('Top 10 Tracks by Average Preference Score')
            axes[1, 0].set_xlabel('Average Preference Score')
            axes[1, 0].set_yticks(range(len(top_tracks)))
            axes[1, 0].set_yticklabels(top_tracks.index)
        
        # Preference by genre (if available)
        if 'genre' in self.df.columns:
            genre_preference = self.df.groupby('genre')['preference_score'].mean().sort_values(ascending=False)
            axes[1, 1].bar(range(len(genre_preference)), genre_preference.values)
            axes[1, 1].set_title('Average Preference Score by Genre')
            axes[1, 1].set_xlabel('Genre')
            axes[1, 1].set_ylabel('Average Preference Score')
            axes[1, 1].set_xticks(range(len(genre_preference)))
            axes[1, 1].set_xticklabels(genre_preference.index, rotation=45)
        
        plt.tight_layout()
        plt.show()
    
    def generate_data_report(self, save_path=None):
        """Generate comprehensive data exploration report"""
        print("📊 Data Exploration Report")
        print("=" * 50)
        
        # Basic info
        print(f"\n📈 Dataset Overview:")
        print(f"   Total records: {len(self.df):,}")
        print(f"   Total columns: {len(self.df.columns)}")
        print(f"   Memory usage: {self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Missing data
        missing_data = self.df.isnull().sum()
        missing_pct = (missing_data / len(self.df)) * 100
        
        print(f"\n🔍 Missing Data Analysis:")
        for col in missing_data[missing_data > 0].index:
            print(f"   {col}: {missing_data[col]:,} ({missing_pct[col]:.1f}%)")
        
        # Data types
        print(f"\n📋 Data Types:")
        dtype_counts = self.df.dtypes.value_counts()
        for dtype, count in dtype_counts.items():
            print(f"   {dtype}: {count} columns")
        
        # Time range
        if 'ts' in self.df.columns:
            print(f"\n⏰ Time Range:")
            print(f"   Start: {self.df['ts'].min()}")
            print(f"   End: {self.df['ts'].max()}")
            print(f"   Duration: {self.df['ts'].max() - self.df['ts'].min()}")
        
        # Summary statistics
        print(f"\n📊 Summary Statistics:")
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            summary = self.df[numeric_cols].describe()
            print(summary.round(2))
        
        # Save report
        if save_path:
            report_data = {
                'dataset_info': {
                    'total_records': len(self.df),
                    'total_columns': len(self.df.columns),
                    'memory_usage_mb': float(self.df.memory_usage(deep=True).sum() / 1024**2)
                },
                'missing_data': missing_data.to_dict(),
                'data_types': dtype_counts.to_dict(),
                'summary_stats': summary.to_dict() if len(numeric_cols) > 0 else None
            }
            
            import json
            with open(save_path, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            print(f"\n💾 Report saved to {save_path}")


if __name__ == "__main__":
    print("🎨 Data Visualization Utilities")
    print("This module provides comprehensive visualization tools for music data.")
    print("Use DataVisualizer class to explore your dataset.")
