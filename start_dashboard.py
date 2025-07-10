#!/usr/bin/env python3
"""
Dashboard Startup Script
Starts both the FastAPI backend and React frontend for VelocityIQ Dashboard
"""

import os
import sys
import subprocess
import time
from dotenv import load_dotenv
import signal
import threading
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python dependencies
    try:
        import fastapi
        import uvicorn
        import psycopg2
        print("✅ Python dependencies are installed")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("📦 Install with: pip install -r requirements_dashboard.txt")
        return False
    
    # Check Node.js and npm
    try:
        subprocess.run(['node', '--version'], check=True, capture_output=True)
        subprocess.run(['npm', '--version'], check=True, capture_output=True)
        print("✅ Node.js and npm are installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js and npm are required")
        print("📦 Install from: https://nodejs.org/")
        return False
    
    return True

def check_environment():
    """Check if environment variables are set"""
    load_dotenv(dotenv_path=".env")
    print("🔍 Checking environment configuration...")
    
    required_vars = [
        'SUPABASE_HOST',
        'SUPABASE_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("📝 Please set these in your .env file")
        return False
    
    print("✅ Environment configuration is valid")
    return True

def install_react_dependencies():
    """Install React dependencies if needed"""
    dashboard_dir = Path('dashboard')
    package_json = dashboard_dir / 'package.json'
    node_modules = dashboard_dir / 'node_modules'
    
    if not package_json.exists():
        print("❌ React dashboard not found. Please ensure dashboard/ directory exists.")
        return False
    
    if not node_modules.exists():
        print("📦 Installing React dependencies...")
        try:
            subprocess.run(['npm', 'install'], cwd=dashboard_dir, check=True)
            print("✅ React dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install React dependencies")
            return False
    
    return True

def start_api_server():
    """Start the FastAPI backend server"""
    print("🚀 Starting API server...")
    try:
        # Use uvicorn to start the FastAPI app
        os.environ['PYTHONPATH'] = os.getcwd()
        subprocess.run([
            sys.executable, '-m', 'uvicorn',
            'dashboard_api:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload'
        ], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to start API server")
        return False
    except KeyboardInterrupt:
        print("\n⏹️  API server stopped")
        return True

def start_react_dev_server():
    """Start the React development server"""
    print("🚀 Starting React development server...")
    dashboard_dir = Path('dashboard')
    try:
        subprocess.run(['npm', 'start'], cwd=dashboard_dir, check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to start React development server")
        return False
    except KeyboardInterrupt:
        print("\n⏹️  React development server stopped")
        return True

def main():
    """Main startup function"""
    print("🏭 VelocityIQ Dashboard Startup")
    print("=" * 50)
    
    # Check dependencies and environment
    if not check_dependencies():
        sys.exit(1)
    
    if not check_environment():
        sys.exit(1)
    
    if not install_react_dependencies():
        sys.exit(1)
    
    print("\n🎯 Starting dashboard services...")
    print("📊 API will be available at: http://localhost:8000")
    print("🖥️  Frontend will be available at: http://localhost:3000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop all services\n")
    
    # Start services in separate processes
    api_process = None
    react_process = None
    
    try:
        # Start API server
        api_process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn',
            'dashboard_api:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload'
        ])
        
        # Wait a moment for API to start
        time.sleep(3)
        
        # Start React development server
        dashboard_dir = Path('dashboard')
        try:
            react_process = subprocess.Popen(['npm', 'start'], cwd=dashboard_dir)
            print("✅ Both services started successfully!")
            print("🌐 Opening dashboard in your browser...")
        except Exception as e:
            print(f"❌ Failed to start React development server: {e}")
            print("Please try running the dashboard again.")
            return False
        
        # Wait for both processes
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if api_process.poll() is not None:
                print("❌ API server stopped unexpectedly")
                break
            
            if react_process.poll() is not None:
                print("❌ React server stopped unexpectedly")
                break
    
    except KeyboardInterrupt:
        print("\n⏹️  Stopping dashboard services...")
    
    finally:
        # Clean up processes
        if api_process:
            try:
                api_process.terminate()
                api_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                api_process.kill()
        
        if react_process:
            try:
                react_process.terminate()
                react_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                react_process.kill()
        
        print("✅ Dashboard services stopped")

if __name__ == "__main__":
    main()
