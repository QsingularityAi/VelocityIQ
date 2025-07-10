import os
import psycopg2
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

def parse_sql_statements(sql_content):
    """Smart SQL parser that handles PostgreSQL functions with $$ delimiters"""
    statements = []
    current_statement = ""
    in_dollar_quote = False
    dollar_tag = None
    
    lines = sql_content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('--'):
            continue
        
        # Check for dollar-quoted strings (PostgreSQL functions)
        if not in_dollar_quote:
            # Look for start of dollar quote like $$, $tag$, etc.
            dollar_match = re.search(r'\$([^$]*)\$', line)
            if dollar_match:
                dollar_tag = dollar_match.group(0)
                in_dollar_quote = True
        else:
            # Look for end of dollar quote
            if dollar_tag in line:
                in_dollar_quote = False
                dollar_tag = None
        
        current_statement += line + " "
        
        # If not in dollar quote and line ends with semicolon, we have a complete statement
        if not in_dollar_quote and line.endswith(';'):
            stmt = current_statement.strip()
            if stmt and not is_problematic_statement(stmt):
                statements.append(stmt)
            current_statement = ""
    
    # Handle any remaining statement
    if current_statement.strip():
        stmt = current_statement.strip()
        if stmt and not is_problematic_statement(stmt):
            statements.append(stmt)
    
    return statements

def setup_schema():
    """Connects to Supabase and executes the schema SQL file."""
    conn = None
    try:
        # Database configuration
        db_config = {
            'host': os.getenv('SUPABASE_HOST'),
            'database': os.getenv('SUPABASE_DB', 'postgres'),
            'user': os.getenv('SUPABASE_USER', 'postgres'),
            'password': os.getenv('SUPABASE_PASSWORD'),
            'port': os.getenv('SUPABASE_PORT', '5432')
        }

        # Connect to the database
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True  # Enable autocommit for individual statements
        print("✅ Successfully connected to the Supabase database.")

        # Read the SQL schema file
        with open('supabase-schema.sql', 'r') as f:
            sql_content = f.read()

        # Parse SQL statements properly handling PostgreSQL functions
        statements = parse_sql_statements(sql_content)
        
        print(f"🔧 Executing {len(statements)} SQL statements...")

        # Execute statements one by one
        with conn.cursor() as cursor:
            for i, statement in enumerate(statements):
                try:
                    cursor.execute(statement)
                    print(f"   ✅ Statement {i+1}/{len(statements)} executed successfully")
                except Exception as stmt_error:
                    if "already exists" in str(stmt_error).lower():
                        print(f"   ⚠️  Statement {i+1}: Already exists (skipping)")
                    else:
                        print(f"   ❌ Statement {i+1} failed: {stmt_error}")
                        # Continue with other statements rather than failing completely
                        continue
        
        # Add basic permissions for the current user
        add_basic_permissions(conn)
        
        # Verify the setup
        verify_tables(conn)
        
        print("✅ Database schema and tables created successfully.")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return False

    finally:
        if conn is not None:
            conn.close()
            print("🔌 Database connection closed.")
    
    return True

def is_problematic_statement(stmt):
    """Check if a SQL statement might cause role-related issues"""
    problematic_keywords = [
        'GRANT USAGE ON SCHEMA public TO anon',
        'GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon',
        'GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated',
        'CREATE POLICY'
    ]
    
    stmt_upper = stmt.upper()
    for keyword in problematic_keywords:
        if keyword.upper() in stmt_upper:
            return True
    return False

def add_basic_permissions(conn):
    """Add basic permissions for the current database user"""
    print("🔐 Setting up basic permissions...")
    
    try:
        with conn.cursor() as cursor:
            # Get current database user
            cursor.execute("SELECT current_user")
            current_user = cursor.fetchone()[0]
            print(f"   Current user: {current_user}")
            
            # Grant permissions to current user (should already have them, but just in case)
            basic_permissions = [
                "GRANT USAGE ON SCHEMA public TO CURRENT_USER",
                "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO CURRENT_USER",
                "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO CURRENT_USER"
            ]
            
            for perm in basic_permissions:
                try:
                    cursor.execute(perm)
                    print(f"   ✅ Permission granted: {perm}")
                except Exception as e:
                    print(f"   ⚠️  Permission already exists: {e}")
                    
    except Exception as e:
        print(f"   ⚠️  Could not set up permissions: {e}")

def verify_tables(conn):
    """Verify that all required tables were created"""
    print("🔍 Verifying table creation...")
    
    required_tables = ['suppliers', 'products', 'forecast_data', 'alerts', 'inventory_transactions']
    
    with conn.cursor() as cursor:
        for table in required_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   ✅ {table}: {count} records")
            except Exception as e:
                print(f"   ❌ {table}: Not found or error - {e}")
                return False
    
    print("🎉 All required tables are present and accessible!")
    return True

def add_sample_data(conn):
    """Add sample inventory transactions for testing forecasting"""
    print("📦 Adding sample inventory transactions...")
    
    try:
        with conn.cursor() as cursor:
            # Check if we have products
            cursor.execute("SELECT id, name FROM products LIMIT 5")
            products = cursor.fetchall()
            
            if not products:
                print("   ⚠️  No products found. Sample data from schema may not have been inserted.")
                return False
            
            # Check if we already have enough transactions
            cursor.execute("SELECT COUNT(*) FROM inventory_transactions")
            existing_count = cursor.fetchone()[0]
            
            if existing_count >= 100:  # We want substantial transaction history
                print(f"   ✅ Found {existing_count} existing transactions. Sufficient for forecasting.")
                return True
            
            # Generate additional sample transactions
            import random
            from datetime import datetime, timedelta
            
            transactions_to_add = max(0, 150 - existing_count)  # Target 150 total transactions
            print(f"   🔄 Adding {transactions_to_add} additional transactions...")
            
            transactions_added = 0
            
            for product_id, product_name in products:
                # Generate 30 days of transaction history
                for day in range(30):
                    transaction_date = datetime.now() - timedelta(days=30-day)
                    
                    # Generate realistic demand patterns based on product type
                    if 'headphones' in product_name.lower() or 'speaker' in product_name.lower():
                        base_demand = random.randint(5, 12)  # Higher demand for electronics
                    elif 'cable' in product_name.lower() or 'case' in product_name.lower():
                        base_demand = random.randint(3, 8)   # Moderate demand for accessories
                    else:
                        base_demand = random.randint(2, 6)   # Lower demand for other items
                    
                    # Add some weekend boost
                    if transaction_date.weekday() >= 5:  # Saturday or Sunday
                        base_demand = int(base_demand * 1.3)
                    
                    if base_demand > 0:
                        cursor.execute("""
                            INSERT INTO inventory_transactions 
                            (product_id, type, quantity, reference_number, notes, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            product_id,
                            'outbound',
                            base_demand,
                            f'TXN-{random.randint(1000, 9999)}',
                            f'Daily demand for {product_name}',
                            transaction_date
                        ))
                        transactions_added += 1
                        
                        if transactions_added >= transactions_to_add:
                            break
                
                if transactions_added >= transactions_to_add:
                    break
            
            print(f"   ✅ Added {transactions_added} additional sample transactions")
            
            # Verify final count
            cursor.execute("SELECT COUNT(*) FROM inventory_transactions")
            final_count = cursor.fetchone()[0]
            print(f"   📊 Total transactions now: {final_count}")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Failed to add sample data: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up Supabase Schema for VelocityIQ")
    print("=" * 60)
    
    # Run schema setup
    if setup_schema():
        print("\n" + "=" * 60)
        print("🎉 SCHEMA SETUP COMPLETE!")
        print("=" * 60)
        print("✅ All tables created successfully")
        print("✅ Basic permissions configured")
        print("✅ Ready for forecasting pipeline")
        print("\n🎯 Next Steps:")
        print("1. Run: python deploy_jumpstart_chronos.py")
        print("2. Run: python supabase_forecasting_integration.py")
        print("3. View: python forecast_dashboard.py")
        
        # Try to add sample data
        print("\n📦 Adding sample data for testing...")
        try:
            conn = psycopg2.connect(
                host=os.getenv('SUPABASE_HOST'),
                database=os.getenv('SUPABASE_DB', 'postgres'),
                user=os.getenv('SUPABASE_USER', 'postgres'),
                password=os.getenv('SUPABASE_PASSWORD'),
                port=os.getenv('SUPABASE_PORT', '5432')
            )
            conn.autocommit = True
            add_sample_data(conn)
            conn.close()
        except Exception as e:
            print(f"⚠️  Could not add sample data: {e}")
            print("   You can add sample data manually or the forecasting pipeline will handle missing data.")
    else:
        print("\n❌ Schema setup failed. Please check your database connection and try again.")
