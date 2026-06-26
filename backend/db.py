import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData

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

def get_clean_products_table():
    if 'clean_products' in metadata.tables:
        return metadata.tables['clean_products']
    else:
        raise ValueError("clean_products table not found in database. Run setup_db.py and clean_data.py first.")
