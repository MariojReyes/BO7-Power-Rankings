from supabase import create_client
from dotenv import load_dotenv
import os
print("WORKING DIR:", os.getcwd())


load_dotenv()

url = os.getenv("SUPABASE_URL")              
key = os.getenv("SUPABASE_SERVICE_KEY")      

supabase = create_client(url, key)

# test insert
result = supabase.table("matches").insert({
    "by_who": "Mario",
    "map_id": 1,
    "mode_id": 1,
    "guild_score": 250,
    "jsoc_score": 240
}).execute()

print(result)
