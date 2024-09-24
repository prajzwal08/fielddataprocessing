import os
import pandas as pd
import zipfile
import json
from typing import List, Optional, Dict

# File locations
file_location = "/home/khanalp/data/field_data/"
data_location = "/home/khanalp/code/PhD/fielddataprocessing/data/"

# Open the JSON file and load it into a dictionary
with open(os.path.join(data_location, "location_dict.json"), 'r') as f:
    dict_location = json.load(f)

def unzip_files(folder_path: str) -> None:
    """Unzip all zip files in the specified folder."""
    zip_files = [filename for filename in os.listdir(folder_path) if filename.endswith('.zip')]
    if zip_files:
        for filename in zip_files:
            zip_file_path = os.path.join(folder_path, filename)
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(folder_path)
            print(f"Unzipped: {zip_file_path}")
    else:
        print(f"No zip files found in: {folder_path}")

def find_csv_file(logger_id: str, file_location: str) -> Optional[str]:
    """Find the appropriate CSV file based on logger_id."""
    return next(
        (os.path.join(folder_path, filename)
         for folder_path, _, filenames in os.walk(file_location)
         for filename in filenames
         if filename.endswith('.csv') and logger_id in filename and "Configuration 2-" in filename),
        next((os.path.join(folder_path, filename)
              for folder_path, _, filenames in os.walk(file_location)
              for filename in filenames
              if filename.endswith('.csv') and logger_id in filename and "Configuration 1-" in filename),
             None)
    )



# # Unzip files in the specified file_location
# for folder in os.listdir(file_location):
#     folder_path = os.path.join(file_location, folder)
#     if os.path.isdir(folder_path):
#         unzip_files(folder_path)


# Iterate over location_dict and process each logger_id
for location, loggers in dict_location.items():
    print(location)
    for logger_name, logger_info in loggers.items():
        logger_id = logger_info['logger_id']
        depths = logger_info['depths']
        print(logger_name)
        print(logger_id)
        print(depths)
        if logger_id != 'z6-08822':
            """Process CSV file based on logger_id, rename columns, and save to output directory."""
            data_file_location = find_csv_file(logger_id, file_location)

            if data_file_location is None:
                print(f"No file found for logger_id: {logger_id}")
            # Load the CSV file
            data_frame = pd.read_csv(data_file_location)

            # Process headers (assuming headers are misaligned)
            data_frame.columns = data_frame.iloc[1, :]
            data_frame = data_frame[3:].reset_index(drop=True)

                    # Initialize a dictionary to map column types to their new names
            depth_map = {depth: f"{depth}cm" for depth in depths}

            # Create a mapping for the new column names
            new_columns = []

            # Track the indices for moisture and temperature
            moisture_index, temperature_index = 0, 0
            # Iterate over the existing columns and create new column names
            for col in data_frame.columns:
                if 'm³/m³ Water Content' in col:
                    new_columns.append(f"soil_moisture_{depth_map[depths[moisture_index]]}")
                    moisture_index += 1
                elif '°C Soil Temperature' in col:
                    new_columns.append(f"soil_temperature_{depth_map[depths[temperature_index]]}")
                    temperature_index += 1
                else:
                    new_columns.append(col)  # Keep original name if no match

            # Assign the new column names to the DataFrame
            data_frame.columns = new_columns

            # Save the processed file
            output_file_name = f"{logger_id}_processed.csv"
            output_file_path = os.path.join(data_location, output_file_name)
            data_frame.to_csv(output_file_path, index=False)
            print(f"Processed and saved: {output_file_path}")
