import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def connect_to_db():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

def fetch_data():
    client = connect_to_db()
    data = client.table("products").select("*").execute()
    return data.data
