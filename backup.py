import os
import csv
from datetime import datetime

# Source folder
src_folder = r"C:\TEMP\bck"

# Output files
photos_csv = "add_photos.csv"
videos_csv = "add_videos.csv"

# Common headers
headers = ["camera", "date", "filename", "location", "time", "url"]

def get_file_date(path):
    """Return file modification date as YYYY-MM-DD"""
    ts = os.path.getmtime(path)
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")

def process_files():
    photos = []
    videos = []

    for fname in os.listdir(src_folder):
        fpath = os.path.join(src_folder, fname)
        if not os.path.isfile(fpath):
            continue

        name, ext = os.path.splitext(fname)
        ext = ext.lower()

        if ext == ".jpg":
            photos.append({
                "camera": "OldSamsung",
                "date": get_file_date(fpath),
                "filename": name,
                "location": "Mauritius",
                "time": "NA",
                "url": "NA"
            })
        elif ext == ".mp4":
            videos.append({
                "camera": "OldSamsung",
                "date": get_file_date(fpath),
                "filename": name,
                "location": "Mauritius",
                "time": "NA",
                "url": "NA"
            })

    # Write photos CSV
    with open(photos_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(photos)

    # Write videos CSV
    with open(videos_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(videos)

if __name__ == "__main__":
    process_files()
    print(f"CSV files created: {photos_csv}, {videos_csv}")