#libraries
import os
import requests
import pandas as pd
import sys
import matplotlib.pyplot as plt

# dataset URL
URL = "https://raw.githubusercontent.com/rushi4git/spotify-playlist-data/main/spotify_playlist.json"

OUTPUT_DIR = "/opt/airflow/output" # Directory to save raw and transformed datasets, reports, and charts

RAW_FILE = os.path.join(OUTPUT_DIR, "playlist_raw.csv")
TRANSFORMED_FILE = os.path.join(OUTPUT_DIR, "playlist_transformed.csv")


def generate_dataset_statistics(df):
    stats_path = os.path.join(OUTPUT_DIR, "dataset_statistics.txt")

    total_tracks = len(df)
    unique_artists = df["artist_name"].nunique()
    unique_albums = df["album_name"].nunique()

    avg_popularity = df["popularity"].mean()
    avg_duration = df["duration_minutes"].mean()
    
    earliest_release = df["release_date"].min()
    latest_release = df["release_date"].max()

    with open(stats_path, "w") as f:
        f.write("Spotify Playlist Dataset Statistics\n")
        f.write("------------------------------------\n\n")

        f.write(f"Total tracks: {total_tracks}\n")
        f.write(f"Unique artists: {unique_artists}\n")
        f.write(f"Unique albums: {unique_albums}\n")
        f.write(f"Average popularity: {avg_popularity:.2f}\n")
        f.write(f"Average duration (minutes): {avg_duration:.2f}\n")
        f.write(f"Earliest release: {earliest_release}\n")
        f.write(f"Latest release: {latest_release}\n")

    print("Dataset statistics generated ")


# Task 1: Fetch Spotify data
def fetch_data():

    print("Fetching Spotify data...")

    response = requests.get(URL)  # Make a GET request to the dataset URL
    data = response.json() 

    df = pd.DataFrame(data["tracks"])

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df.to_csv(RAW_FILE, index=False)

    print("Raw dataset saved")
    

# Task 2: Validate dataset
def validate_data():
    print("Validating dataset...")

    df = pd.read_csv(RAW_FILE)

    required_columns = ["track_name", "artist_name", "album_name", "popularity", "duration_ms", "release_date"]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
        
        if df.empty:
            raise ValueError("Dataset is empty")
        
        if df["popularity"].min() < 0 or df["popularity"].max() > 100:  # Popularity should be between 0 and 100
            raise ValueError("Popularity values must be between 0 and 100")

    if df.isnull().values.any():
        print("Warning: Missing values found in the dataset")
    else:
        print("No missing values found")

    print("Dataset validation completed successfully")

    

# Task 3: Transform dataset
def transform_data():

    print("Transforming dataset...")

    df = pd.read_csv(RAW_FILE)

    df = df.dropna()

    df["duration_minutes"] = df["duration_ms"] / 60000   # Convert duration from milliseconds to minutes

    df.to_csv(TRANSFORMED_FILE, index=False)

    print("Transformed dataset saved")
    


# Task 4: Generate summary report and charts
def generate_report():

    print("Generating summary report...")

    df = pd.read_csv(TRANSFORMED_FILE)

    summary_path = os.path.join(OUTPUT_DIR, "summary_report.txt")

    top_tracks = df.nlargest(5, "popularity")[["track_name", "artist_name", "popularity"]]  # Get top 5 most popular tracks

    avg_duration = df["duration_minutes"].mean()

    most_frequent_artist = df["artist_name"].value_counts().idxmax()

    with open(summary_path, "w") as f:

        f.write("Spotify Playlist Data Summary Report\n")
        f.write("=" * 40 + "\n\n")   # Write a header for the summary report

        f.write(f"Total tracks: {len(df)}\n")
        f.write(f"Average track duration (minutes): {avg_duration:.2f}\n")
        f.write(f"Most frequent artist: {most_frequent_artist}\n\n")

        f.write("Top 5 Most Popular Tracks:\n")
        f.write(top_tracks.to_string(index=False))

    print("Summary Report Generated!!!")
    generate_dataset_statistics(df)
    


    #Top artists chart
    artist_counts = df["artist_name"].value_counts().head(10)
    plt.figure(figsize=(10, 6))
    artist_counts.plot(kind="bar")
    plt.title("Top Artists in Spotify Playlist")
    plt.xlabel("Artist")
    plt.ylabel("Number of Tracks")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "top_artists.png"))
    plt.close()
    print("Top artists chart saved")


    #Duration distribution chart
    plt.figure(figsize=(10, 6))
    df["duration_minutes"].hist(bins=20)
    plt.title("Distribution of Track Durations")
    plt.xlabel("Duration (minutes)")
    plt.ylabel("Number of Tracks")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "duration_distribution.png"))
    plt.close()
    print("Duration distribution chart saved")



if __name__ == "__main__":

    task = sys.argv[1]

    if task == "fetch":
        fetch_data()

    elif task == "validate":
        validate_data()

    elif task == "transform":
        transform_data()

    elif task == "report":
        generate_report()

    elif task =="notify":
        print("Notification: Spotify playlist pipeline completed successfully!")