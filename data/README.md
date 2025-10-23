# Data Directory

This directory contains the raw and processed data for the music recommendation engine.

## Structure

- `raw/` - Original, unprocessed data files
- `processed/` - Cleaned and feature-engineered datasets

## Data Requirements

The model expects CSV files with the following columns:

### Required Columns
- `ts` - Timestamp of the listening event
- `ms_played` - Milliseconds played
- `duration_ms` - Total duration of the track
- `id` - Unique track identifier
- `track` - Track name
- `artist` - Artist name

### Audio Features (Optional but Recommended)
- `popularity` - Track popularity score
- `danceability`, `energy`, `valence` - Audio characteristics
- `tempo`, `loudness` - Audio properties
- `acousticness`, `instrumentalness` - Audio analysis

### Behavioral Features
- `reason_start` - How playback started
- `reason_end` - How playback ended
- `skipped` - Whether track was skipped

## Sample Data

Place your listening history CSV in `raw/` directory. The model will process it and create feature-engineered versions in `processed/`.
