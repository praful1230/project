from llama_index.core import SQLDatabase, NLSQLTableQueryEngine
from sqlalchemy import create_engine
import pandas as pd

def query_to_chart(query):
    engine = create_engine("sqlite:///wms.db")  # Export Baserow to SQLite or use direct connection
    sql_database = SQLDatabase(engine, include_tables=["products", "orders", "returns"])
    
    query_engine = NLSQLTableQueryEngine(sql_database=sql_database)
    response = query_engine.query(query)
    
    # Convert response to chart data
    df = pd.DataFrame(response.data)
    return {
        "labels": df.iloc[:, 0].tolist(),
        "values": df.iloc[:, 1].tolist() if len(df.columns) > 1 else []
    }

# Example usage
if __name__ == "__main__":
    result = query_to_chart("Show total sales by MSKU")
    print(result)