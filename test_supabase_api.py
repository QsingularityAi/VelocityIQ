#!/usr/bin/env python3
"""
Test Supabase API Access
Simple test to verify your Supabase project is accessible
"""

import os
import requests
from dotenv import load_dotenv

def test_supabase_api():
    """Test if Supabase API is accessible"""
    
    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env")
        return False
    
    print("🔍 Testing Supabase API access...")
    print(f"📍 URL: {supabase_url}")
    
    try:
        # Test API endpoint
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}'
        }
        
        response = requests.get(
            f"{supabase_url}/rest/v1/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Supabase API is accessible!")
            print("📊 Project is active and responding")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    if test_supabase_api():
        print("\n🔄 Now try the database connection test:")
        print("python test_db_connection.py")
    else:
        print("\n❌ Fix Supabase access first") 