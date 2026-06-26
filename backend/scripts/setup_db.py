import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, MetaData, Table
from sqlalchemy.dialects.postgresql import JSONB

load_dotenv()

uri = os.getenv("SUPABASE_URI")

# Ensure the password is URL-encoded if it contains special characters like '@'
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

raw_products = Table(
    'raw_products', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('source_file', String),
    Column('raw_data', JSONB)
)

clean_products = Table(
    'clean_products', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String, nullable=False),
    Column('brand', String),
    Column('price_usd', Float),
    Column('rating', Float),
    Column('category', String),
    Column('ram', String),
    Column('storage', String),
    Column('specs_summary', Text)
)

def setup():
    print("Dropping existing tables (if any)...")
    metadata.drop_all(engine)
    print("Creating tables: raw_products, clean_products...")
    metadata.create_all(engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    setup()
