import pandas as pd
import glob

# Get all CSV files from the 'cleaned' folder
csv_files = glob.glob("cleaned/*.csv")

# Read and combine all CSV files
dfs = []
for file in csv_files:
    df = pd.read_csv(file)
    dfs.append(df)

# Combine all dataframes
combined_df = pd.concat(dfs, ignore_index=True)

# Save to new CSV file
combined_df.to_csv("data.csv", index=False)

print(f"Successfully combined {len(csv_files)} CSV files into 'data.csv'")
print(f"Total rows in combined file: {len(combined_df)}")
