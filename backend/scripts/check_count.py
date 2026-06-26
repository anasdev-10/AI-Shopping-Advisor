import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

uri = os.getenv("SUPABASE_URI")
if uri and "@" in uri:
    parts = uri.split('@')
    if len(parts) > 2:
        cred = '@'.join(parts[:-1])
        host_part = parts[-1]
        cred_parts = cred[13:].split(':')
        user = cred_parts[0]
        password = ':'.join(cred_parts[1:])
        uri = f"postgresql://{user}:{urllib.parse.quote(password)}@{host_part}"

engine = create_engine(uri)
with engine.connect() as conn:
    result = conn.execute(text("SELECT count(*) FROM raw_products"))
    print("Rows in raw_products:", result.scalar())
