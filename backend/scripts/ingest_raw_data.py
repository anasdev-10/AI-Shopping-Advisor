import os
import glob
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

uri = os.getenv("SUPABASE_URI")

if uri and "@" in uri:
    parts = uri.split('@')
    if len(parts) > 2:
        cred = '@'.join(parts[:-1])
        host_part = parts[-1]
        if cred.startswith("postgresql://"):
            cred_parts = cred[13:].split(':')
            user = cred_parts[0]
            password = ':'.join(cred_parts[1:])
            encoded_password = urllib.parse.quote(password)
            uri = f"postgresql://{user}:{encoded_password}@{host_part}"

engine = create_engine(uri)
metadata = MetaData()
metadata.reflect(bind=engine)

def clean_val(val):
    if pd.isna(val):
        return None
    if isinstance(val, str):
        return val.replace('\x00', '')
    return val

def ingest_data():
    if 'raw_products' not in metadata.tables:
        print("Error: raw_products table not found in database. Run setup_db.py first.")
        return

    raw_products = metadata.tables['raw_products']
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw')
    csv_files = glob.glob(os.path.join(data_dir, '*.csv'))
    
    with engine.begin() as conn:
        for file in csv_files:
            filename = os.path.basename(file)
            print(f"Ingesting {filename}...")
            df = pd.read_csv(file)
            
            records = df.to_dict(orient='records')
            
            insert_data = []
            for record in records:
                clean_record = {k: clean_val(v) for k, v in record.items()}
                insert_data.append({'source_file': filename, 'raw_data': clean_record})
            
            # Use chunked insertions in case of large lists
            for i in range(0, len(insert_data), 1000):
                conn.execute(raw_products.insert(), insert_data[i:i+1000])
            print(f"Inserted {len(insert_data)} rows from {filename}.")

if __name__ == "__main__":
    ingest_data()
