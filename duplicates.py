import pandas as pd

# Files to compare
file1 = "bckp_photos.csv"
file2 = "photos - 20251209.csv"

# Columns of interest
cols = ["camera", "date", "filename", "location", "time", "url"]

# Read both CSVs
df1 = pd.read_csv(file1, usecols=cols)
df2 = pd.read_csv(file2, usecols=cols)

# Add a column to track source file
df1["source"] = file1
df2["source"] = file2

# Combine into one DataFrame
df = pd.concat([df1, df2], ignore_index=True)

# Find duplicates in the 'filename' column across both files
duplicates = df[df.duplicated("filename", keep=False)]

# Group duplicates by filename for clarity
grouped = duplicates.groupby("filename")

# Print results
for fname, group in grouped:
    print(f"\nDuplicate filename: {fname}")
    print(group.to_string(index=False))