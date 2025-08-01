import requests
import pandas as pd

BASEROW_TOKEN = "Sf2jubJOlpeXt2eUGSzKN7oe0i77nqBu"
BASE_URL = "https://api.baserow.io/api/database/"

def create_table(database_id, table_name, fields):
    response = requests.post(
        f"{BASE_URL}tables/",
        headers={"Authorization": f"Token {BASEROW_TOKEN}"},
        json={"name": table_name, "database_id": database_id}
    )
    table_id = response.json()["id"]
    
    for field in fields:
        requests.post(
            f"{BASE_URL}fields/table/{table_id}/",
            headers={"Authorization": f"Token {BASEROW_TOKEN}"},
            json=field
        )
    return table_id

def import_data(table_id, data_file):
    df = pd.read_csv(data_file)
    for _, row in df.iterrows():
        requests.post(
            f"{BASE_URL}rows/table/{table_id}/",
            headers={"Authorization": f"Token {BASEROW_TOKEN}"},
            json=row.to_dict()
        )

# Initialize tables
database_id = "268106"
tables = {
    "Products": [
        {"name": "MSKU", "type": "text", "primary": True},
        {"name": "SKU", "type": "text"},
        {"name": "Name", "type": "text"},
        {"name": "Category", "type": "text"},
        {"name": "Opening Stock", "type": "number"}
    ],
    "Orders": [
        {"name": "Order ID", "type": "text", "primary": True},
        {"name": "MSKU", "type": "link_row", "link_row_table": "Products"},
        {"name": "Date", "type": "date"},
        {"name": "Quantity", "type": "number"},
        {"name": "Revenue", "type": "number"}
    ],
    "Returns": [
        {"name": "Return ID", "type": "text", "primary": True},
        {"name": "Order ID", "type": "link_row", "link_row_table": "Orders"},
        {"name": "Reason", "type": "text"},
        {"name": "Date", "type": "date"}
    ],
    "Inventory": [
        {"name": "MSKU", "type": "text", "primary": True},
        {"name": "Current Stock", "type": "number"}
    ]
}

table_ids = {}
for table_name, fields in tables.items():
    table_ids[table_name] = create_table(database_id, table_name, fields)

# Import data
import_data(table_ids["Orders"], "mapped_sales_data.csv")
import_data(table_ids["Products"], "mappings.csv")