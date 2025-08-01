from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from sku_mapper import SKUMapper
from fetch_wms_sheet import fetch_wms_sheet
from fetch_sales_data import fetch_sales_data
import pandas as pd
import requests
import os
import tkinter as tk
from tkinter import filedialog, messagebox

app = FastAPI()

# GUI for SKU Mapping
class SKUMapperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WMS SKU Mapper")
        self.mapper = None
        tk.Button(root, text="Fetch WMS Sheet", command=self.fetch_wms).pack(pady=10)
        tk.Button(root, text="Fetch Sales Data", command=self.fetch_sales).pack(pady=10)
        tk.Button(root, text="Process Sales Data", command=self.process_sales).pack(pady=10)

    def fetch_wms(self):
        sheet_url = "https://docs.google.com/spreadsheets/d/1ORu33oTA1KcLMkyjmujcBjdzfavOnkUJJJKxujFq2Fw/edit"
        mapping_file = fetch_wms_sheet(sheet_url)
        if mapping_file:
            self.mapper = SKUMapper(mapping_file)
            messagebox.showinfo("Success", "WMS Sheet fetched and loaded!")
        else:
            messagebox.showerror("Error", "Failed to fetch WMS Sheet")

    def fetch_sales(self):
        folder_id = "1mzaLpJprXKxwSDI0_Ej157h5dbNKn5y4"
        self.sales_file = fetch_sales_data(folder_id)
        if self.sales_file:
            messagebox.showinfo("Success", "Sales Data fetched!")
        else:
            messagebox.showerror("Error", "Failed to fetch Sales Data")

    def process_sales(self):
        if not self.mapper or not hasattr(self, 'sales_file'):
            messagebox.showerror("Error", "Load WMS Sheet and Sales Data first!")
            return
        result = self.mapper.process_sales_data(self.sales_file)
        result.to_csv("mapped_sales_data.csv", index=False)
        messagebox.showinfo("Success", "Sales data processed and saved!")

# FastAPI Endpoints
@app.post("/fetch-and-process")
async def fetch_and_process():
    sheet_url = "https://docs.google.com/spreadsheets/d/1ORu33oTA1KcLMkyjmujcBjdzfavOnkUJJJKxujFq2Fw/edit"
    folder_id = "1mzaLpJprXKxwSDI0_Ej157h5dbNKn5y4"
    
    mapping_file = fetch_wms_sheet(sheet_url)
    sales_file = fetch_sales_data(folder_id)
    
    if not mapping_file or not sales_file:
        return {"message": "Failed to fetch data"}
    
    mapper = SKUMapper(mapping_file)
    result = mapper.process_sales_data(sales_file)
    
    # Update Baserow inventory
    BASEROW_TOKEN = "YOUR_BASEROW_TOKEN"
    BASEROW_TABLE_ID = "YOUR_TABLE_ID"
    for _, row in result.groupby('MSKU').agg({'Quantity': 'sum'}).reset_index().iterrows():
        msku, qty = row['MSKU'], row['Quantity']
        requests.patch(
            f"https://api.baserow.io/api/database/rows/table/{BASEROW_TABLE_ID}/{msku}/",
            json={"Current Stock": f"Current Stock - {qty}"},
            headers={"Authorization": f"Token {BASEROW_TOKEN}"}
        )
    
    output_file = "output.csv"
    result.to_csv(output_file, index=False)
    return FileResponse(output_file, filename="mapped_sales_data.csv")

@app.post("/process-sales")
async def process_sales(file: UploadFile = File(...)):
    # Existing endpoint for manual uploads (unchanged)
    mapper = SKUMapper("mappings.csv")
    temp_file = f"temp_{file.filename}"
    with open(temp_file, "wb") as f:
        f.write(await file.read())
    result = mapper.process_sales_data(temp_file)
    
    BASEROW_TOKEN = "YOUR_BASEROW_TOKEN"
    BASEROW_TABLE_ID = "YOUR_TABLE_ID"
    for _, row in result.groupby('MSKU').agg({'Quantity': 'sum'}).reset_index().iterrows():
        msku, qty = row['MSKU'], row['Quantity']
        requests.patch(
            f"https://api.baserow.io/api/database/rows/table/{BASEROW_TABLE_ID}/{msku}/",
            json={"Current Stock": f"Current Stock - {qty}"},
            headers={"Authorization": f"Token {BASEROW_TOKEN}"}
        )
    
    output_file = "output.csv"
    result.to_csv(output_file, index=False)
    os.remove(temp_file)
    return FileResponse(output_file, filename="mapped_sales_data.csv")

@app.get("/metrics")
async def get_metrics():
    BASEROW_TOKEN = "YOUR_BASEROW_TOKEN"
    TABLE_ID = "YOUR_ORDERS_TABLE_ID"
    response = requests.get(
        f"https://api.baserow.io/api/database/rows/table/{TABLE_ID}/",
        headers={"Authorization": f"Token {BASEROW_TOKEN}"}
    )
    data = response.json()
    df = pd.DataFrame(data)
    sales_by_msku = df.groupby('MSKU').agg({'Revenue': 'sum'}).reset_index()
    return {
        "labels": sales_by_msku['MSKU'].tolist(),
        "values": sales_by_msku['Revenue'].tolist()
    }

if __name__ == "__main__":
    root = tk.Tk()
    app_gui = SKUMapperGUI(root)
    root.mainloop()