#!/usr/bin/env python3
"""
Setup script for VelocityIQ Dashboard with Real Supabase Data
This will install dependencies and test your database connection
"""

import subprocess
import sys
import os
from pathlib import Path

def install_supabase():
    """Install Supabase Python client"""
    print("📦 Installing Supabase Python client...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'supabase'])
        print("✅ Supabase client installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Supabase client: {e}")
        return False

def check_env_file():
    """Check if .env file exists with required variables"""
    print("🔍 Checking .env file...")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = []
    
    with open('.env', 'r') as f:
        content = f.read()
        for var in required_vars:
            if f"{var}=" not in content:
                missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ .env file looks good")
    return True

def test_supabase_connection():
    """Test connection to Supabase"""
    print("🔌 Testing Supabase connection...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from supabase import create_client, Client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            print("❌ Missing SUPABASE_URL or SUPABASE_KEY")
            return False
        
        supabase: Client = create_client(url, key)
        
        # Test with a simple query
        response = supabase.table('products').select('id').limit(1).execute()
        
        if response.data is not None:
            print("✅ Successfully connected to Supabase!")
            print(f"📊 Found products table with data")
            return True
        else:
            print("⚠️ Connected but no data found. Database might be empty.")
            return True
            
    except ImportError:
        print("❌ Supabase client not installed")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def check_database_schema():
    """Check if the required tables exist"""
    print("📋 Checking database schema...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from supabase import create_client, Client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        supabase: Client = create_client(url, key)
        
        required_tables = ['products', 'suppliers', 'forecast_data', 'alerts', 'inventory_transactions']
        existing_tables = []
        missing_tables = []
        
        for table in required_tables:
            try:
                response = supabase.table(table).select('*').limit(1).execute()
                if response.data is not None:
                    existing_tables.append(table)
                    print(f"  ✅ {table}")
                else:
                    missing_tables.append(table)
                    print(f"  ❌ {table}")
            except Exception:
                missing_tables.append(table)
                print(f"  ❌ {table}")
        
        if missing_tables:
            print(f"\n⚠️ Missing tables: {', '.join(missing_tables)}")
            print("💡 You need to run the schema setup SQL in your Supabase dashboard")
            print("   File: supabase-schema.sql")
            return False
        else:
            print("✅ All required tables exist!")
            return True
            
    except Exception as e:
        print(f"❌ Schema check failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🏭 VelocityIQ Dashboard Setup - Real Data")
    print("=" * 50)
    
    success = True
    
    # Step 1: Install Supabase client
    if not install_supabase():
        success = False
    
    # Step 2: Check environment file
    if not check_env_file():
        success = False
    
    # Step 3: Test connection
    if success and not test_supabase_connection():
        success = False
    
    # Step 4: Check schema
    if success and not check_database_schema():
        success = False
    
    print("\n" + "=" * 50)
    
    if success:
        print("🎉 Setup completed successfully!")
        print("🚀 You can now run: python dashboard_api_fixed.py")
        print("📊 Your dashboard will use real Supabase data!")
    else:
        print("❌ Setup incomplete. Please fix the issues above.")
        print("\n💡 Quick fixes:")
        print("   1. Make sure .env file has SUPABASE_URL and SUPABASE_KEY")
        print("   2. Run supabase-schema.sql in your Supabase dashboard")
        print("   3. Check your internet connection")
    
    return success

if __name__ == "__main__":
    main() 