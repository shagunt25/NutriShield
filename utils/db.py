import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("❌ Error: SUPABASE_URL or SUPABASE_KEY is missing in .env file")

# Initialize the client
supabase: Client = create_client(url, key)
print("✅ Connected to Supabase successfully")