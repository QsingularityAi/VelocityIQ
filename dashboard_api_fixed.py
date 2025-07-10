#!/usr/bin/env python3
"""
Fixed Dashboard API for VelocityIQ
This version uses the correct table names and columns from your actual Supabase schema
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Load environment variables
load_dotenv()

app = FastAPI(title="VelocityIQ Dashboard API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
# Use service role key for backend API (bypasses RLS for admin operations)
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

# Initialize Supabase client
try:
    from supabase import create_client, Client
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables")
        SUPABASE_AVAILABLE = False
        supabase = None
    else:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        SUPABASE_AVAILABLE = True
        print("✅ Supabase client initialized successfully")
        print(f"🔑 Using service role key: {SUPABASE_KEY[:20]}...") if SUPABASE_KEY else None
except ImportError:
    SUPABASE_AVAILABLE = False
    print("❌ Supabase client not available. Run: pip install supabase")
    supabase = None
except Exception as e:
    SUPABASE_AVAILABLE = False
    print(f"❌ Supabase initialization failed: {e}")
    supabase = None

@app.get("/")
async def root():
    return {
        "message": "VelocityIQ Dashboard API", 
        "status": "running",
        "supabase_available": SUPABASE_AVAILABLE,
        "schema_version": "v1.0 - Fixed for real Supabase schema"
    }

@app.get("/api/dashboard/overview")
async def get_dashboard_overview():
    """Get high-level dashboard overview metrics using real schema"""
    if not SUPABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Supabase client not available")
    
    try:
        # Get total products
        products_response = supabase.table('products').select('id', count='exact').execute()
        total_products = products_response.count if hasattr(products_response, 'count') else len(products_response.data or [])
        
        # Get low stock products (current_stock <= reorder_point)
        # Since we can't easily compare two columns with simple filter, get all products and filter in Python
        all_products_response = supabase.table('products').select('id, current_stock, reorder_point').execute()
        low_stock_products = 0
        if all_products_response.data:
            for product in all_products_response.data:
                current_stock = product.get('current_stock', 0) or 0
                reorder_point = product.get('reorder_point', 0) or 0
                if current_stock <= reorder_point:
                    low_stock_products += 1
        
        # Get critical alerts (unresolved with high/critical severity)
        alerts_response = supabase.table('alerts').select('id').eq('is_resolved', False).in_('severity', ['high', 'critical']).execute()
        critical_alerts = len(alerts_response.data or [])
        
        # Get total inventory value
        inventory_response = supabase.table('products').select('current_stock, unit_cost').execute()
        total_inventory_value = 0
        if inventory_response.data:
            for item in inventory_response.data:
                if item.get('current_stock') and item.get('unit_cost'):
                    total_inventory_value += float(item['current_stock']) * float(item['unit_cost'])
        
        # Get future forecast records
        today = datetime.now().date().isoformat()
        forecast_response = supabase.table('forecast_data').select('id', count='exact').gte('date', today).execute()
        forecast_records = forecast_response.count if hasattr(forecast_response, 'count') else len(forecast_response.data or [])
        
        return {
            "total_products": total_products,
            "low_stock_products": low_stock_products,
            "critical_alerts": critical_alerts,
            "total_inventory_value": float(total_inventory_value),
            "forecast_records": forecast_records,
            "last_updated": datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"Overview query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@app.get("/api/dashboard/alerts")
async def get_alerts():
    """Get current alerts using real schema"""
    if not SUPABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Supabase client not available")
    
    try:
        # Get unresolved alerts with product and supplier info
        response = supabase.table('alerts').select('''
            id,
            type,
            severity,
            title,
            description,
            created_at,
            product_id,
            supplier_id,
            products(name, sku),
            suppliers(name)
        ''').eq('is_resolved', False).order('created_at', desc=True).limit(20).execute()
        
        alerts = []
        if response.data:
            for alert in response.data:
                product_info = alert.get('products') or {}
                supplier_info = alert.get('suppliers') or {}
                
                alerts.append({
                    "id": alert.get('id'),
                    "type": alert.get('type'),
                    "severity": alert.get('severity'),
                    "title": alert.get('title'),
                    "description": alert.get('description'),
                    "created_at": alert.get('created_at'),
                    "product_name": product_info.get('name'),
                    "sku": product_info.get('sku'),
                    "supplier_name": supplier_info.get('name')
                })
        
        return {"alerts": alerts}
    
    except Exception as e:
        print(f"Alerts query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@app.get("/api/dashboard/stock-status")
async def get_stock_status():
    """Get current stock status using real schema"""
    if not SUPABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Supabase client not available")
    
    try:
        # Get products with supplier info and calculate averages
        response = supabase.table('products').select('''
            id,
            name,
            sku,
            category,
            current_stock,
            reorder_point,
            unit_cost,
            suppliers(name, lead_time_days, reliability_score)
        ''').execute()
        
        products = []
        if response.data:
            for product in response.data:
                current_stock = product.get('current_stock', 0)
                reorder_point = product.get('reorder_point', 0)
                supplier_info = product.get('suppliers') or {}
                
                # Calculate average daily demand from recent forecast data
                try:
                    forecast_response = supabase.table('forecast_data').select('predicted_demand').eq('product_id', product['id']).gte('date', (datetime.now() - timedelta(days=7)).date().isoformat()).execute()
                    
                    if forecast_response.data:
                        demands = [float(f.get('predicted_demand', 0)) for f in forecast_response.data]
                        avg_daily_demand = sum(demands) / len(demands) if demands else 0
                    else:
                        avg_daily_demand = 0
                except:
                    avg_daily_demand = 0
                
                # Calculate days until stockout
                days_until_stockout = current_stock / avg_daily_demand if avg_daily_demand > 0 else None
                
                # Determine stock status
                if current_stock <= reorder_point:
                    stock_status = "REORDER_NOW"
                elif days_until_stockout and days_until_stockout <= 7:
                    stock_status = "LOW_STOCK"
                elif days_until_stockout and days_until_stockout <= 14:
                    stock_status = "MONITOR"
                else:
                    stock_status = "OK"
                
                products.append({
                    "id": product.get('id'),
                    "product_name": product.get('name'),
                    "sku": product.get('sku'),
                    "category": product.get('category'),
                    "current_stock": current_stock,
                    "reorder_point": reorder_point,
                    "unit_cost": float(product.get('unit_cost', 0)),
                    "avg_daily_demand": round(avg_daily_demand, 2),
                    "days_until_stockout": round(days_until_stockout, 1) if days_until_stockout else None,
                    "stock_status": stock_status,
                    "supplier_name": supplier_info.get('name'),
                    "lead_time_days": supplier_info.get('lead_time_days'),
                    "reliability_score": float(supplier_info.get('reliability_score', 0))
                })
        
        return {"products": products}
    
    except Exception as e:
        print(f"Stock status query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@app.get("/api/dashboard/forecasts")
async def get_forecasts(days: int = 14):
    """Get forecast data using real schema"""
    if not SUPABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Supabase client not available")
    
    try:
        start_date = datetime.now().date().isoformat()
        end_date = (datetime.now() + timedelta(days=days)).date().isoformat()
        
        response = supabase.table('forecast_data').select('''
            date,
            predicted_demand,
            confidence_interval_lower,
            confidence_interval_upper,
            created_at,
            products(name, sku, category, current_stock)
        ''').gte('date', start_date).lte('date', end_date).order('date').execute()
        
        forecasts = []
        if response.data:
            for forecast in response.data:
                product_info = forecast.get('products') or {}
                
                forecasts.append({
                    "product_name": product_info.get('name'),
                    "sku": product_info.get('sku'),
                    "category": product_info.get('category'),
                    "current_stock": product_info.get('current_stock'),
                    "forecast_date": forecast.get('date'),
                    "predicted_demand": float(forecast.get('predicted_demand', 0)),
                    "confidence_interval_lower": float(forecast.get('confidence_interval_lower', 0)),
                    "confidence_interval_upper": float(forecast.get('confidence_interval_upper', 0)),
                    "forecast_created": forecast.get('created_at')
                })
        
        return {"forecasts": forecasts}
    
    except Exception as e:
        print(f"Forecasts query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@app.get("/api/dashboard/demand-trends")
async def get_demand_trends():
    """Get demand trend analysis using real schema"""
    if not SUPABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Supabase client not available")
    
    try:
        # Get recent forecast data to calculate trends
        start_date = (datetime.now() - timedelta(days=14)).date().isoformat()
        
        response = supabase.table('forecast_data').select('''
            date,
            predicted_demand,
            products(name, sku, category)
        ''').gte('date', start_date).order('date').execute()
        
        # Process data to calculate trends
        trends_data = {}
        if response.data:
            for item in response.data:
                product_info = item.get('products') or {}
                product_name = product_info.get('name')
                
                if product_name not in trends_data:
                    trends_data[product_name] = {
                        'product_info': product_info,
                        'data_points': []
                    }
                
                trends_data[product_name]['data_points'].append({
                    'date': item.get('date'),
                    'predicted_demand': float(item.get('predicted_demand', 0))
                })
        
        # Calculate change percentages
        trends = []
        for product_name, data in trends_data.items():
            data_points = sorted(data['data_points'], key=lambda x: x['date'])
            
            for i, point in enumerate(data_points):
                # Calculate 7-day change
                week_ago_index = max(0, i - 7)
                if week_ago_index < i:
                    previous_demand = data_points[week_ago_index]['predicted_demand']
                    current_demand = point['predicted_demand']
                    
                    if previous_demand > 0:
                        change_percentage = ((current_demand - previous_demand) / previous_demand) * 100
                    else:
                        change_percentage = 0
                else:
                    change_percentage = None
                
                trends.append({
                    "product_name": product_name,
                    "sku": data['product_info'].get('sku'),
                    "category": data['product_info'].get('category'),
                    "date": point['date'],
                    "predicted_demand": point['predicted_demand'],
                    "demand_7_days_ago": data_points[week_ago_index]['predicted_demand'] if week_ago_index < i else None,
                    "change_percentage": round(change_percentage, 1) if change_percentage is not None else None
                })
        
        return {"trends": trends}
    
    except Exception as e:
        print(f"Trends query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@app.get("/api/dashboard/chart-data/{product_sku}")
async def get_product_chart_data(product_sku: str):
    """Get detailed chart data for a specific product using real schema"""
    if not SUPABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Supabase client not available")
    
    try:
        # Get product ID first
        product_response = supabase.table('products').select('id').eq('sku', product_sku).execute()
        if not product_response.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product_id = product_response.data[0]['id']
        
        # Get historical data from inventory transactions
        historical_start = (datetime.now() - timedelta(days=30)).date().isoformat()
        transactions_response = supabase.table('inventory_transactions').select('''
            created_at,
            type,
            quantity
        ''').eq('product_id', product_id).gte('created_at', historical_start).order('created_at').execute()
        
        # Process historical data (aggregate daily outbound transactions as demand)
        historical = {}
        if transactions_response.data:
            for txn in transactions_response.data:
                date = txn['created_at'][:10]  # Extract date part
                if txn['type'] == 'outbound':
                    if date not in historical:
                        historical[date] = 0
                    historical[date] += txn['quantity']
        
        historical_data = [
            {"date": date, "actual_demand": demand}
            for date, demand in sorted(historical.items())
        ]
        
        # Get future forecasts
        today = datetime.now().date().isoformat()
        end_date = (datetime.now() + timedelta(days=14)).date().isoformat()
        
        forecast_response = supabase.table('forecast_data').select('''
            date,
            predicted_demand,
            confidence_interval_lower,
            confidence_interval_upper
        ''').eq('product_id', product_id).gte('date', today).lte('date', end_date).order('date').execute()
        
        forecast_data = []
        if forecast_response.data:
            for forecast in forecast_response.data:
                forecast_data.append({
                    "date": forecast.get('date'),
                    "predicted_demand": float(forecast.get('predicted_demand', 0)),
                    "confidence_interval_lower": float(forecast.get('confidence_interval_lower', 0)),
                    "confidence_interval_upper": float(forecast.get('confidence_interval_upper', 0))
                })
        
        return {
            "product_sku": product_sku,
            "historical": historical_data,
            "forecasts": forecast_data
        }
    
    except Exception as e:
        print(f"Chart data query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting VelocityIQ Dashboard API (Fixed for Real Schema)...")
    print(f"📊 Supabase Available: {SUPABASE_AVAILABLE}")
    print("📚 API docs at: http://localhost:8000/docs")
    print("✅ Using correct table names and schema!")
    
    uvicorn.run(
        "dashboard_api_fixed:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 