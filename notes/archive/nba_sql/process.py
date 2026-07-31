import csv
import json
import os

# print(os.getcwd())

csv_file_path = r"C:\Users\akuck\Downloads\archive\nba_stats_25-26.csv"
output_txt_path = 'output_data.txt'

# 1. Read the CSV into a list of dicts
with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file)
    list_of_dicts = list(reader)

# 2. Output the list of dicts to a text file
with open(output_txt_path, mode='w', encoding='utf-8') as txt_file:
    # indent=4 makes the file human-readable; omit it for a single-line file
    json.dump(list_of_dicts, txt_file, indent=4)

print(f"Successfully saved data to {output_txt_path}")

