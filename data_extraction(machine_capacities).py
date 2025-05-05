import pandas as pd

# Load the Excel file (now that you have pandas & openpyxl installed)
df = pd.read_excel('machine_capacities.xlsx', engine='openpyxl')

# Save to JSON
json_path = 'machine_capacities.json'
df.to_json(json_path, orient='records', force_ascii=False)
print(f"Wrote {len(df)} records to {json_path}")
