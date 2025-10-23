#!/usr/bin/env python3
"""
Setup script for the music recommendation engine.

This script helps users set up the project environment, install dependencies,
and configure the system for optimal performance.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def create_directories():
    """Create necessary directories"""
    directories = [
        'data/raw',
        'data/processed',
        'models',
        'notebooks',
        'logs',
        'static',
        'templates'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")


def install_dependencies():
    """Install Python dependencies"""
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return False
    
    # Install additional development dependencies
    dev_deps = [
        "black",  # Code formatting
        "flake8",  # Linting
        "pre-commit"  # Git hooks
    ]
    
    for dep in dev_deps:
        run_command(f"pip install {dep}", f"Installing {dep}")
    
    return True


def setup_git_hooks():
    """Setup Git hooks for code quality"""
    if not Path('.git').exists():
        print("⚠️  Not a Git repository. Skipping Git hooks setup.")
        return True
    
    # Install pre-commit hooks
    if run_command("pre-commit install", "Installing pre-commit hooks"):
        print("✅ Git hooks configured for code quality")
        return True
    return False


def create_sample_files():
    """Create sample configuration and data files"""
    # Create sample config
    from src.config import create_sample_config
    create_sample_config()
    
    # Create sample data
    sample_data = """ts,ms_played,duration_ms,id,track,artist,popularity,danceability,energy,valence
2024-01-01 10:30:00,180000,180000,track_001,Sample Song 1,Sample Artist 1,75,0.7,0.8,0.6
2024-01-01 11:15:00,120000,200000,track_002,Sample Song 2,Sample Artist 2,60,0.5,0.6,0.7
2024-01-01 12:00:00,90000,150000,track_003,Sample Song 3,Sample Artist 3,85,0.8,0.9,0.8"""
    
    with open('data/raw/sample_data.csv', 'w') as f:
        f.write(sample_data)
    
    print("📄 Created sample files:")
    print("   - config.json (configuration)")
    print("   - data/raw/sample_data.csv (sample data)")


def run_tests():
    """Run tests to verify installation"""
    print("🧪 Running tests to verify installation...")
    
    # Run unit tests
    if run_command("python run_tests.py --unit", "Running unit tests"):
        print("✅ Unit tests passed")
    else:
        print("⚠️  Unit tests failed - check your installation")
    
    # Run integration tests
    if run_command("python run_tests.py --integration", "Running integration tests"):
        print("✅ Integration tests passed")
    else:
        print("⚠️  Integration tests failed - check your installation")


def setup_web_app():
    """Setup web application"""
    print("🌐 Setting up web application...")
    
    # Check if Flask is installed
    try:
        import flask
        print("✅ Flask is installed")
    except ImportError:
        print("❌ Flask not found. Installing...")
        if not run_command("pip install flask", "Installing Flask"):
            return False
    
    print("✅ Web application setup complete")
    print("   Run 'python web_app.py' to start the web interface")
    return True


def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description='Setup music recommendation engine')
    parser.add_argument('--skip-tests', action='store_true', help='Skip running tests')
    parser.add_argument('--skip-web', action='store_true', help='Skip web app setup')
    parser.add_argument('--dev', action='store_true', help='Setup for development')
    
    args = parser.parse_args()
    
    print("🎵 Music Recommendation Engine Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    print("\n📁 Creating project directories...")
    create_directories()
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Setup Git hooks (if in Git repo)
    if args.dev:
        print("\n🔧 Setting up development environment...")
        setup_git_hooks()
    
    # Create sample files
    print("\n📄 Creating sample files...")
    create_sample_files()
    
    # Setup web app
    if not args.skip_web:
        print("\n🌐 Setting up web application...")
        setup_web_app()
    
    # Run tests
    if not args.skip_tests:
        print("\n🧪 Running tests...")
        run_tests()
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Place your listening data in data/raw/")
    print("2. Run 'python train.py --data data/raw/your_data.csv' to train a model")
    print("3. Run 'python web_app.py' to start the web interface")
    print("4. Visit http://localhost:5000 to use the web interface")
    
    if args.dev:
        print("\nDevelopment tools:")
        print("- Run 'black .' to format code")
        print("- Run 'flake8 .' to check code quality")
        print("- Run 'python run_tests.py --coverage' for coverage report")


if __name__ == "__main__":
    main()

