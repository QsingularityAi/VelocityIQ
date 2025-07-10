#!/usr/bin/env python3
"""
Setup and Configuration Script for Custom Chronos-Bolt Supply Chain Forecasting
Validates prerequisites and helps configure the environment
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple

def check_python_version() -> bool:
    """Check if Python version is 3.8 or higher"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
        return False

def check_package_installation() -> Tuple[List[str], List[str]]:
    """Check if required packages are installed"""
    required_packages = [
        'torch', 'transformers', 'pandas', 'numpy', 'datasets',
        'boto3', 'sagemaker', 'supabase', 'matplotlib', 'seaborn'
    ]
    
    installed = []
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            installed.append(package)
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}")
    
    return installed, missing

def install_missing_packages(missing_packages: List[str]) -> bool:
    """Install missing packages"""
    if not missing_packages:
        return True
    
    print(f"\nInstalling missing packages: {', '.join(missing_packages)}")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements.txt"
        ])
        print("✅ Successfully installed missing packages")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages")
        return False

def check_aws_credentials() -> bool:
    """Check AWS credentials configuration"""
    try:
        import boto3
        session = boto3.Session()
        credentials = session.get_credentials()
        
        if credentials is None:
            print("❌ AWS credentials not found")
            print("   Configure with: aws configure")
            print("   Or set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
            return False
        
        # Test SageMaker access
        sagemaker_client = boto3.client('sagemaker')
        sagemaker_client.list_endpoints(MaxResults=1)
        
        print("✅ AWS credentials configured and SageMaker accessible")
        return True
        
    except Exception as e:
        print(f"❌ AWS configuration issue: {e}")
        return False

def check_environment_variables() -> Dict[str, bool]:
    """Check required environment variables"""
    required_vars = {
        'SUPABASE_URL': os.getenv('SUPABASE_URL'),
        'SUPABASE_ANON_KEY': os.getenv('SUPABASE_ANON_KEY')
    }
    
    results = {}
    for var, value in required_vars.items():
        if value:
            print(f"✅ {var}")
            results[var] = True
        else:
            print(f"❌ {var}")
            results[var] = False
    
    return results

def create_env_template():
    """Create a .env template file"""
    template = """# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# AWS Configuration (optional if using AWS CLI)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1

# Optional: Weights & Biases for experiment tracking
WANDB_API_KEY=your_wandb_key
"""
    
    with open('.env.template', 'w') as f:
        f.write(template)
    
    print("✅ Created .env.template file")
    print("   Copy to .env and fill in your actual values")

def test_supabase_connection() -> bool:
    """Test Supabase connection"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not set")
        return False
    
    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)
        
        # Test connection by trying to query a table
        response = supabase.table("products").select("id").limit(1).execute()
        
        print("✅ Supabase connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

def check_gpu_availability() -> bool:
    """Check if GPU is available for training"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✅ GPU available: {gpu_name} ({gpu_count} device(s))")
            return True
        else:
            print("⚠️  No GPU detected (CPU training will be slower)")
            return False
    except:
        print("❌ Cannot check GPU availability")
        return False

def check_disk_space() -> bool:
    """Check available disk space"""
    try:
        import shutil
        free_space = shutil.disk_usage('.').free / (1024**3)  # GB
        
        if free_space >= 10:
            print(f"✅ Disk space: {free_space:.1f} GB available")
            return True
        else:
            print(f"⚠️  Low disk space: {free_space:.1f} GB (recommended: 10+ GB)")
            return False
    except:
        print("❌ Cannot check disk space")
        return False

def validate_supabase_schema() -> bool:
    """Validate that the Supabase schema is properly set up"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Cannot validate schema: Supabase credentials not set")
        return False
    
    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)
        
        required_tables = ['suppliers', 'products', 'forecast_data', 'alerts', 'inventory_transactions']
        
        for table in required_tables:
            try:
                response = supabase.table(table).select("*").limit(1).execute()
                print(f"✅ Table '{table}' exists")
            except Exception as e:
                print(f"❌ Table '{table}' missing or inaccessible: {e}")
                return False
        
        print("✅ Supabase schema validation successful")
        return True
        
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False

def create_project_structure():
    """Create necessary project directories"""
    directories = [
        'models',
        'data',
        'logs',
        'visualizations'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def main():
    """Main setup function"""
    print("=" * 60)
    print("CUSTOM CHRONOS-BOLT SETUP AND VALIDATION")
    print("=" * 60)
    
    all_checks_passed = True
    
    # Check Python version
    print("\n🐍 Checking Python version...")
    if not check_python_version():
        all_checks_passed = False
    
    # Check package installation
    print("\n📦 Checking package installation...")
    installed, missing = check_package_installation()
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        if input("Install missing packages? (y/n): ").lower() == 'y':
            if not install_missing_packages(missing):
                all_checks_passed = False
        else:
            all_checks_passed = False
    
    # Check system resources
    print("\n💻 Checking system resources...")
    check_gpu_availability()
    check_disk_space()
    
    # Check AWS configuration
    print("\n☁️  Checking AWS configuration...")
    if not check_aws_credentials():
        all_checks_passed = False
        print("   Setup AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html")
    
    # Check environment variables
    print("\n🔐 Checking environment variables...")
    env_results = check_environment_variables()
    
    if not all(env_results.values()):
        print("\n⚠️  Some environment variables are missing")
        if not os.path.exists('.env.template'):
            create_env_template()
        print("   1. Copy .env.template to .env")
        print("   2. Fill in your Supabase credentials")
        print("   3. Run this setup script again")
        all_checks_passed = False
    
    # Test Supabase connection
    if all(env_results.values()):
        print("\n🗄️  Testing Supabase connection...")
        if not test_supabase_connection():
            all_checks_passed = False
        else:
            print("\n📋 Validating Supabase schema...")
            if not validate_supabase_schema():
                all_checks_passed = False
                print("   Please run the supabase-schema.sql in your Supabase SQL editor")
    
    # Create project structure
    print("\n📁 Creating project structure...")
    create_project_structure()
    
    # Final summary
    print("\n" + "=" * 60)
    if all_checks_passed:
        print("🎉 SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("You can now run the forecasting pipeline:")
        print("1. python data_extraction.py")
        print("2. python train_chronos_custom.py")
        print("3. python deploy_custom_chronos.py")
        print("4. python supply_chain_forecasting_pipeline.py")
    else:
        print("❌ SETUP INCOMPLETE")
        print("=" * 60)
        print("Please address the issues above and run setup.py again")
    
    print("\n📖 For detailed instructions, see README.md")

if __name__ == "__main__":
    main() 