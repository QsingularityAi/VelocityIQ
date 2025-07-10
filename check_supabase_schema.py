#!/usr/bin/env python3
"""
Check Supabase Database Schema
This script will connect to your Supabase database and show what tables exist
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_supabase_with_client():
    """Check Supabase using Python client"""
    try:
        from supabase import create_client, Client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            print("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env file")
            return False
        
        supabase: Client = create_client(url, key)
        print("✅ Supabase client created successfully")
        
        # Try to query information_schema to see available tables
        try:
            # Get list of tables in public schema
            response = supabase.table('information_schema.tables').select('table_name').eq('table_schema', 'public').execute()
            print(f"📊 Found {len(response.data)} tables:")
            for table in response.data:
                print(f"  - {table['table_name']}")
        except Exception as e:
            print(f"⚠️ Could not query information_schema: {e}")
            
            # Try some common table names
            common_tables = ['products', 'inventory', 'forecasts', 'alerts', 'suppliers', 'current_inventory', 'product_forecasts', 'inventory_alerts']
            print("\n🔍 Checking for common tables:")
            
            for table_name in common_tables:
                try:
                    response = supabase.table(table_name).select('*').limit(1).execute()
                    if response.data is not None:
                        print(f"  ✅ {table_name} - EXISTS")
                        if response.data:
                            columns = list(response.data[0].keys())
                            print(f"      Columns: {', '.join(columns)}")
                    else:
                        print(f"  ❌ {table_name} - Not found")
                except Exception as table_error:
                    print(f"  ❌ {table_name} - Error: {str(table_error)}")
        
        return True
        
    except ImportError:
        print("❌ Supabase client not installed. Run: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

def check_supabase_with_psycopg2():
    """Check Supabase using direct PostgreSQL connection"""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Try direct connection
        conn = psycopg2.connect(
            host=os.getenv('SUPABASE_HOST', 'db.ayzvfkfjexcqebgxqqhw.supabase.co'),
            database=os.getenv('SUPABASE_DB', 'postgres'),
            user=os.getenv('SUPABASE_USER', 'postgres'),
            password=os.getenv('SUPABASE_PASSWORD'),
            port=os.getenv('SUPABASE_PORT', '5432')
        )
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get list of tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        """)
        
        tables = cursor.fetchall()
        print(f"📊 Found {len(tables)} tables via PostgreSQL:")
        
        for table in tables:
            table_name = table['table_name']
            print(f"  - {table_name}")
            
            # Get column info
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position
            """, (table_name,))
            
            columns = cursor.fetchall()
            column_info = [f"{col['column_name']}({col['data_type']})" for col in columns]
            print(f"      Columns: {', '.join(column_info)}")
        
        cursor.close()
        conn.close()
        return True
        
    except ImportError:
        print("❌ psycopg2 not installed")
        return False
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def main():
    print("🔍 VelocityIQ Database Schema Check")
    print("=" * 50)
    
    print(f"📍 Supabase URL: {os.getenv('SUPABASE_URL')}")
    print(f"🔑 Has API Key: {'Yes' if os.getenv('SUPABASE_KEY') else 'No'}")
    print()
    
    # Try Supabase client first
    print("Method 1: Supabase Python Client")
    print("-" * 30)
    if not check_supabase_with_client():
        print("\nMethod 2: Direct PostgreSQL Connection")
        print("-" * 30)
        check_supabase_with_psycopg2()

if __name__ == "__main__":
    main() 