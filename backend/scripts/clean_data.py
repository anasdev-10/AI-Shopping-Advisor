import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.orm import Session
import re

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
raw_products = metadata.tables['raw_products']
clean_products = metadata.tables['clean_products']

def extract_category(filename):
    match = re.search(r'us-shein-([a-zA-Z_]+)-\d+\.csv', filename)
    if match:
        return match.group(1).replace('_', ' ')
    return "unknown"

def parse_price(price_str):
    if not price_str or not isinstance(price_str, str):
        return None
    cleaned = re.sub(r'[^\d.]', '', price_str)
    try:
        return float(cleaned)
    except ValueError:
        return None

def clean_data():
    print("Clearing existing clean_products data...")
    with engine.begin() as conn:
        conn.execute(clean_products.delete())

    with Session(engine) as session:
        offset = 0
        limit = 5000
        total_inserted = 0
        
        while True:
            stmt = select(raw_products).offset(offset).limit(limit)
            results = session.execute(stmt).fetchall()
            if not results:
                break
            
            clean_records = []
            for row in results:
                r_id, source_file, raw_data = row.id, row.source_file, row.raw_data
                
                name = raw_data.get("goods-title-link--jump", "")
                if pd.isna(name) if 'pd' in globals() else not name:
                    name = raw_data.get("goods-title-link", "")
                
                if not name or str(name).strip() == "":
                    continue
                    
                price_str = raw_data.get("price", "")
                price_usd = parse_price(price_str)
                
                category = extract_category(source_file)
                selling_prop = raw_data.get("selling_proposition", "")
                
                # Combine name and selling proposition into specs
                specs_summary = f"{name} {selling_prop}".strip()
                
                clean_records.append({
                    "name": str(name),
                    "brand": None,
                    "price_usd": price_usd,
                    "rating": None,
                    "category": category,
                    "ram": None,
                    "storage": None,
                    "specs_summary": specs_summary
                })
            
            if clean_records:
                with engine.begin() as conn:
                    for i in range(0, len(clean_records), 1000):
                        conn.execute(clean_products.insert(), clean_records[i:i+1000])
            
            total_inserted += len(clean_records)
            offset += limit
            print(f"Processed {offset} rows... Inserted {total_inserted} clean records.")

if __name__ == "__main__":
    clean_data()
