from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import pandas as pd
import os

def fetch_sales_data(folder_id):
    try:
        # Authenticate with Google Drive
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()  # Opens browser for authentication
        drive = GoogleDrive(gauth)

        # Query files in the folder
        file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
        sales_files = []

        for file in file_list:
            if file['title'].endswith(('.csv', '.xlsx')):
                # Download file
                file_path = f"temp_{file['title']}"
                file.GetContentFile(file_path)
                sales_files.append(file_path)

        # Combine all sales files
        dfs = []
        for file in sales_files:
            df = pd.read_excel(file) if file.endswith('.xlsx') else pd.read_csv(file)
            dfs.append(df)
            os.remove(file)  # Clean up
        combined_df = pd.concat(dfs, ignore_index=True)
        combined_df.to_csv("sales_data.csv", index=False)
        return "sales_data.csv"
    except Exception as e:
        print(f"Error fetching Sales Data: {str(e)}")
        return None

if __name__ == "__main__":
    folder_id = "1mzaLpJprXKxwSDI0_Ej157h5dbNKn5y4"  # Extracted from Sales Data URL
    fetch_sales_data(folder_id)