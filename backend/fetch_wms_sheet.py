import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

def fetch_wms_sheet(sheet_url):
    try:
        # Authenticate with Google Sheets
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
        client = gspread.authorize(creds)

        # Open the WMS Sheet
        sheet = client.open_by_url(sheet_url).sheet1
        data = sheet.get_all_records()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        df = df[["SKU", "MSKU"]]  # Assuming columns are named SKU and MSKU
        df.to_csv("mappings.csv", index=False)
        return "mappings.csv"
    except Exception as e:
        print(f"Error fetching WMS Sheet: {str(e)}")
        return None

if __name__ == "__main__":
    sheet_url = "https://docs.google.com/spreadsheets/d/1ORu33oTA1KcLMkyjmujcBjdzfavOnkUJJJKxujFq2Fw/edit"
    fetch_wms_sheet(sheet_url)