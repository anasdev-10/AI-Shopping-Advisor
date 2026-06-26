import pandas as pd
import random
from sqlalchemy import text
from db import engine

def generate_laptops(n):
    brands = ['Apple', 'Dell', 'HP', 'Lenovo', 'ASUS', 'Acer', 'Razer', 'MSI']
    models = ['Pro', 'Air', 'XPS', 'Spectre', 'ThinkPad', 'ZenBook', 'Predator', 'Blade', 'Stealth']
    rams = ['8GB', '16GB', '32GB', '64GB']
    storages = ['256GB SSD', '512GB SSD', '1TB SSD', '2TB SSD']
    data = []
    for _ in range(n):
        b = random.choice(brands)
        m = random.choice(models)
        r = random.choice(rams)
        s = random.choice(storages)
        name = f"{b} {m} {random.randint(13, 17)}-inch Premium Laptop"
        price = round(random.uniform(500, 3500), 2)
        rating = round(random.uniform(3.8, 5.0), 1)
        specs = f"High-performance {b} laptop featuring {r} RAM and {s}. Ideal for gaming, programming, and creative work."
        data.append({'name': name, 'brand': b, 'price_usd': price, 'rating': rating, 'category': 'laptops', 'ram': r, 'storage': s, 'specs_summary': specs})
    return data

def generate_smartphones(n):
    brands = ['Apple', 'Samsung', 'Google', 'OnePlus', 'Sony', 'Motorola']
    models = ['iPhone 15', 'Galaxy S24', 'Pixel 8', '12 Pro', 'Xperia 1', 'Edge+']
    rams = ['4GB', '6GB', '8GB', '12GB']
    storages = ['128GB', '256GB', '512GB', '1TB']
    data = []
    for _ in range(n):
        b = random.choice(brands)
        m = random.choice(models)
        r = random.choice(rams)
        s = random.choice(storages)
        name = f"{b} {m} Smartphone {s}"
        price = round(random.uniform(400, 1500), 2)
        rating = round(random.uniform(4.0, 5.0), 1)
        specs = f"The latest {b} smartphone with a stunning OLED display, {r} RAM, and an advanced camera system."
        data.append({'name': name, 'brand': b, 'price_usd': price, 'rating': rating, 'category': 'smartphones', 'ram': r, 'storage': s, 'specs_summary': specs})
    return data

def generate_headphones(n):
    brands = ['Sony', 'Bose', 'Sennheiser', 'Apple', 'Jabra', 'Audio-Technica']
    models = ['WH-1000XM5', 'QuietComfort Ultra', 'Momentum 4', 'AirPods Max', 'Elite 85h', 'ATH-M50xBT']
    data = []
    for _ in range(n):
        b = random.choice(brands)
        m = random.choice(models)
        name = f"{b} {m} Wireless Noise Cancelling Headphones"
        price = round(random.uniform(150, 600), 2)
        rating = round(random.uniform(4.2, 5.0), 1)
        specs = f"Premium over-ear headphones by {b} with industry-leading active noise cancellation and 30-hour battery life."
        data.append({'name': name, 'brand': b, 'price_usd': price, 'rating': rating, 'category': 'headphones', 'ram': None, 'storage': None, 'specs_summary': specs})
    return data

def generate_watches(n):
    brands = ['Apple', 'Samsung', 'Garmin', 'Fitbit', 'Fossil', 'Amazfit']
    models = ['Watch Series 9', 'Galaxy Watch 6', 'Fenix 7', 'Sense 2', 'Gen 6', 'GTR 4']
    data = []
    for _ in range(n):
        b = random.choice(brands)
        m = random.choice(models)
        name = f"{b} {m} Smartwatch"
        price = round(random.uniform(100, 800), 2)
        rating = round(random.uniform(3.9, 5.0), 1)
        specs = f"Advanced smartwatch from {b} tracking heart rate, sleep, and fitness metrics with a durable design."
        data.append({'name': name, 'brand': b, 'price_usd': price, 'rating': rating, 'category': 'smartwatches', 'ram': None, 'storage': None, 'specs_summary': specs})
    return data

def generate_cameras(n):
    brands = ['Sony', 'Canon', 'Nikon', 'Fujifilm', 'Panasonic', 'Leica']
    models = ['Alpha a7 IV', 'EOS R6', 'Z6 II', 'X-T5', 'Lumix S5 II', 'Q3']
    data = []
    for _ in range(n):
        b = random.choice(brands)
        m = random.choice(models)
        name = f"{b} {m} Mirrorless Digital Camera"
        price = round(random.uniform(800, 4000), 2)
        rating = round(random.uniform(4.5, 5.0), 1)
        specs = f"Professional-grade {b} mirrorless camera. Captures 4K video and stunning high-resolution photos."
        data.append({'name': name, 'brand': b, 'price_usd': price, 'rating': rating, 'category': 'cameras', 'ram': None, 'storage': None, 'specs_summary': specs})
    return data

def generate_accessories(n):
    brands = ['Anker', 'Logitech', 'Belkin', 'Razer', 'Corsair', 'Keychron']
    types = ['Wireless Mouse', 'Mechanical Keyboard', 'USB-C Hub', 'Fast Charger', 'Laptop Stand', 'Webcam']
    data = []
    for _ in range(n):
        b = random.choice(brands)
        t = random.choice(types)
        name = f"{b} Premium {t}"
        price = round(random.uniform(20, 150), 2)
        rating = round(random.uniform(4.0, 4.9), 1)
        specs = f"High-quality {t} from {b} designed to enhance your desk setup and improve productivity."
        data.append({'name': name, 'brand': b, 'price_usd': price, 'rating': rating, 'category': 'accessories', 'ram': None, 'storage': None, 'specs_summary': specs})
    return data

def main():
    print("Generating mock data...")
    all_data = []
    all_data.extend(generate_laptops(250))
    all_data.extend(generate_smartphones(250))
    all_data.extend(generate_headphones(250))
    all_data.extend(generate_watches(250))
    all_data.extend(generate_cameras(250))
    all_data.extend(generate_accessories(250))
    
    df = pd.DataFrame(all_data)
    print(f"Generated {len(df)} total products.")
    
    print("Connecting to Supabase and wiping old tables...")
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE clean_products RESTART IDENTITY CASCADE;"))
        try:
            conn.execute(text("TRUNCATE TABLE raw_products RESTART IDENTITY CASCADE;"))
        except Exception:
            pass
    print("Tables cleared successfully.")
    
    print("Uploading premium mock data to Supabase...")
    df.to_sql('clean_products', engine, if_exists='append', index=False, method='multi', chunksize=500)
    print("Upload complete!")

if __name__ == "__main__":
    main()
