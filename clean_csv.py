import pandas as pd
import os

# Read the CSV file with UTF-8 encoding and handle bad lines
df = pd.read_csv("results.csv", encoding="utf-8", on_bad_lines="skip")

# Display the first few rows
print(df.head())

# Save cleaned data as CSV
df.to_csv("cleaned_results.csv", index=False, encoding="utf-8")

# Save cleaned data as Excel
excel_path = "cleaned_results.xlsx"
df.to_excel(excel_path, index=False, engine="openpyxl")

print("✅ Cleaned CSV saved as 'cleaned_results.csv'")
print("✅ Cleaned Excel file saved as 'cleaned_results.xlsx'")

# Open the Excel file automatically (Windows)
os.startfile(excel_path)
