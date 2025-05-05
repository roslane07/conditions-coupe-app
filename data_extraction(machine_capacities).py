import pandas as pd
import json

def validate_machine_capacities(data):
    """Validate machine capacities data structure."""
    if not isinstance(data, list):
        raise ValueError("Machine capacities must be a list")
        
    required_fields = {"n", "power", "torque"}
    for record in data:
        if not isinstance(record, dict):
            raise ValueError("Each record must be a dictionary")
        if not all(field in record for field in required_fields):
            raise ValueError(f"Each record must contain fields: {required_fields}")
        if not all(isinstance(record[field], (int, float)) for field in required_fields):
            raise ValueError("All values must be numbers")
            
    return True

# Load the Excel file
df = pd.read_excel('machine_capacities.xlsx', engine='openpyxl')

# Ensure column names match required format
df.columns = [col.lower() for col in df.columns]  # Convert to lowercase
required_columns = ['n', 'power', 'torque']
if not all(col in df.columns for col in required_columns):
    raise ValueError(f"Excel file must contain columns: {required_columns}")

# Convert to list of dictionaries
data = df[required_columns].to_dict('records')

# Validate data
validate_machine_capacities(data)

# Save to JSON with proper formatting
json_path = 'machine_capacities.json'
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Successfully wrote {len(data)} records to {json_path}")
print("Data format validated successfully.")
