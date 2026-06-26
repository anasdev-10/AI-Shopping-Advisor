**Problem**
Two options for DataPipeline : Either you use one database for everything. You create a raw_products table (where every column is TEXT or JSONB) and a clean_products table with strict data types OR you upload the Kaggle data to MongoDB, pull it into a Python script to clean it, and push it to PostgreSQL.

**Solution**
I choose the 1st Option. Because 1st solutuon has low infrastructure Cost and Network Bottleneck and Maintanence overhead 

