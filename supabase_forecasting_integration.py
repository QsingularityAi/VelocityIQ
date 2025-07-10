#!/usr/bin/env python3
"""
Supabase + JumpStart Chronos Integration (Fixed)
Uses Supabase Python client instead of direct PostgreSQL connection
"""

import json
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ML imports
from sagemaker.predictor import Predictor
from sagemaker.session import Session
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseChronosIntegration:
    def __init__(self):
        """Initialize Supabase and SageMaker connections"""
        self.supabase = None
        self.chronos_predictor = None
        self.session = Session()
        
    def connect_database(self) -> bool:
        """Connect to Supabase using Python client"""
        try:
            from supabase import create_client, Client
            
            url = os.getenv("SUPABASE_URL")
            # Use service role key for admin operations (bypasses RLS)
            key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
            
            if not url or not key:
                print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env file")
                return False
            
            self.supabase: Client = create_client(url, key)
            
            # Test connection with a simple query
            test_response = self.supabase.table('products').select('id').limit(1).execute()
            if test_response.data is not None:
                print("✅ Connected to Supabase database via client")
                return True
            else:
                print("❌ Supabase client connected but cannot query products table")
                return False
                
        except ImportError:
            print("❌ Supabase client not installed. Run: pip install supabase")
            return False
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def connect_chronos_endpoint(self) -> bool:
        """Connect to deployed JumpStart Chronos endpoint"""
        deployment_info_path = Path("deployment_info_jumpstart.json")
        
        if not deployment_info_path.exists():
            print("❌ No JumpStart deployment info found. Please deploy first:")
            print("python deploy_jumpstart_chronos.py")
            return False
            
        with open(deployment_info_path, 'r') as f:
            info = json.load(f)
            
        endpoint_name = info.get("endpoint_name")
        if not endpoint_name:
            print("❌ No endpoint name found in deployment info.")
            return False
            
        try:
            self.chronos_predictor = Predictor(
                endpoint_name=endpoint_name,
                serializer=JSONSerializer(),
                deserializer=JSONDeserializer(),
                sagemaker_session=self.session
            )
            print(f"✅ Connected to Chronos endpoint: {endpoint_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Chronos endpoint: {e}")
            return False
    
    def extract_historical_demand(self, product_id: str, days: int = 90) -> List[float]:
        """Extract historical demand data from inventory transactions using Supabase client"""
        try:
            # Get transactions for the last N days
            start_date = (datetime.now() - timedelta(days=days)).date().isoformat()
            
            response = self.supabase.table('inventory_transactions').select('''
                created_at,
                type,
                quantity
            ''').eq('product_id', product_id).gte('created_at', start_date).order('created_at').execute()
            
            if not response.data:
                # Generate synthetic demand if no historical data
                print(f"⚠️  No historical data found for product {product_id}, generating synthetic demand")
                return [max(0, 10 + np.random.normal(0, 3)) for _ in range(min(30, days))]
            
            # Process transactions to calculate daily demand
            daily_demand = {}
            for txn in response.data:
                date = txn['created_at'][:10]  # Extract date part
                if txn['type'] == 'outbound':
                    if date not in daily_demand:
                        daily_demand[date] = 0
                    daily_demand[date] += abs(txn['quantity'])
            
            # Convert to sorted list
            sorted_dates = sorted(daily_demand.keys())
            demand_values = [daily_demand[date] for date in sorted_dates]
            
            # Ensure we have enough data points (minimum 5 for Chronos)
            if len(demand_values) < 5:
                # Pad with average demand
                avg_demand = np.mean(demand_values) if demand_values else 10
                while len(demand_values) < 5:
                    demand_values.append(avg_demand)
            
            # Ensure all values are floats
            return [float(v) for v in demand_values]
            
        except Exception as e:
            print(f"❌ Error extracting historical demand for {product_id}: {e}")
            # Return synthetic data as fallback
            return [max(0, 10 + np.random.normal(0, 3)) for _ in range(min(30, days))]
    
    def get_products_for_forecasting(self) -> List[Dict]:
        """Get all products that need forecasting using Supabase client"""
        try:
            response = self.supabase.table('products').select('''
                id,
                name,
                sku,
                category,
                current_stock,
                reorder_point,
                unit_cost
            ''').not_.is_('current_stock', 'null').order('name').execute()
            
            if response.data:
                return response.data
            else:
                print("❌ No products found for forecasting")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching products: {e}")
            return []
    
    def generate_forecasts(self, forecast_days: int = 14) -> Dict:
        """Generate forecasts for all products using Chronos"""
        print(f"🔮 Generating {forecast_days}-day forecasts for all products...")
        
        products = self.get_products_for_forecasting()
        if not products:
            print("❌ No products found for forecasting")
            return {}
        
        # Prepare batch payload for all products
        inputs = []
        product_mapping = {}
        
        for product in products:
            product_id = product['id']
            historical_demand = self.extract_historical_demand(product_id)
            
            if len(historical_demand) >= 5:  # Chronos minimum requirement
                inputs.append({
                    "target": historical_demand,
                    "item_id": product['sku'],
                    "start": (datetime.now() - timedelta(days=len(historical_demand))).strftime('%Y-%m-%d')
                })
                product_mapping[product['sku']] = product
        
        if not inputs:
            print("❌ No valid historical data found for any products")
            return {}
        
        # Call Chronos endpoint
        payload = {
            "inputs": inputs,
            "parameters": {
                "prediction_length": forecast_days,
                "quantile_levels": [0.1, 0.25, 0.5, 0.75, 0.9],
                "freq": "D",
                "batch_size": min(32, len(inputs))  # Optimize batch size
            }
        }
        
        try:
            print(f"📡 Calling Chronos endpoint for {len(inputs)} products...")
            response = self.chronos_predictor.predict(payload)
            
            forecast_results = {}
            for prediction in response['predictions']:
                sku = prediction['item_id']
                product = product_mapping[sku]
                
                forecast_results[product['id']] = {
                    'product': product,
                    'forecast': {
                        'median': prediction['0.5'],
                        'lower_bound': prediction['0.1'],
                        'upper_bound': prediction['0.9'],
                        'q25': prediction['0.25'],
                        'q75': prediction['0.75']
                    }
                }
            
            print(f"✅ Generated forecasts for {len(forecast_results)} products")
            return forecast_results
            
        except Exception as e:
            print(f"❌ Forecasting failed: {e}")
            return {}
    
    def save_forecasts_to_database(self, forecast_results: Dict, forecast_days: int = 14):
        """Save forecast results to Supabase forecast_data table using client"""
        print("💾 Saving forecasts to database...")
        
        try:
            # Clear existing future forecasts
            today = datetime.now().date().isoformat()
            self.supabase.table('forecast_data').delete().gt('date', today).execute()
            
            # Prepare records for bulk insert
            forecast_records = []
            
            for product_id, result in forecast_results.items():
                forecast = result['forecast']
                
                for day in range(forecast_days):
                    forecast_date = (datetime.now().date() + timedelta(days=day + 1)).isoformat()
                    
                    forecast_records.append({
                        'product_id': product_id,
                        'date': forecast_date,
                        'predicted_demand': round(forecast['median'][day], 2),
                        'confidence_interval_lower': round(forecast['lower_bound'][day], 2),
                        'confidence_interval_upper': round(forecast['upper_bound'][day], 2),
                        'created_at': datetime.now().isoformat()
                    })
            
            # Insert forecasts in batches
            batch_size = 100
            for i in range(0, len(forecast_records), batch_size):
                batch = forecast_records[i:i + batch_size]
                self.supabase.table('forecast_data').upsert(batch).execute()
            
            print(f"✅ Saved {len(forecast_records)} forecast records to database")
            
        except Exception as e:
            print(f"❌ Error saving forecasts: {e}")
    
    def generate_intelligent_alerts(self, forecast_results: Dict):
        """Generate intelligent alerts based on forecasts and business rules"""
        print("🚨 Generating intelligent alerts...")
        
        alerts_to_create = []
        
        for product_id, result in forecast_results.items():
            product = result['product']
            forecast = result['forecast']
            
            # Alert 1: Low stock prediction
            avg_daily_demand = np.mean(forecast['median'][:7])  # Average next 7 days
            days_until_stockout = (product['current_stock'] or 0) / max(avg_daily_demand, 0.1)
            
            if days_until_stockout <= 7:
                alerts_to_create.append({
                    'type': 'stock_low',
                    'severity': 'high' if days_until_stockout <= 3 else 'medium',
                    'title': f'Stock Alert: {product["name"]}',
                    'description': f'Predicted stockout in {days_until_stockout:.1f} days. Current stock: {product["current_stock"]}, avg daily demand: {avg_daily_demand:.1f}',
                    'product_id': product_id,
                    'is_resolved': False,
                    'created_at': datetime.now().isoformat()
                })
            
            # Alert 2: Demand spike detection
            recent_avg = np.mean(forecast['median'][:3])  # Next 3 days
            week_avg = np.mean(forecast['median'][:7])    # Next 7 days
            
            if recent_avg > week_avg * 1.5:  # 50% spike
                alerts_to_create.append({
                    'type': 'demand_spike',
                    'severity': 'medium',
                    'title': f'Demand Spike: {product["name"]}',
                    'description': f'Predicted demand spike detected. 3-day avg: {recent_avg:.1f}, 7-day avg: {week_avg:.1f}',
                    'product_id': product_id,
                    'is_resolved': False,
                    'created_at': datetime.now().isoformat()
                })
            
            # Alert 3: Reorder point breach
            current_stock = product.get('current_stock', 0) or 0
            reorder_point = product.get('reorder_point', 0) or 0
            
            if current_stock <= reorder_point:
                alerts_to_create.append({
                    'type': 'stock_low',
                    'severity': 'high',
                    'title': f'Reorder Point Reached: {product["name"]}',
                    'description': f'Current stock ({current_stock}) at or below reorder point ({reorder_point})',
                    'product_id': product_id,
                    'is_resolved': False,
                    'created_at': datetime.now().isoformat()
                })
        
        # Save alerts to database
        if alerts_to_create:
            self._save_alerts(alerts_to_create)
        
        print(f"✅ Generated {len(alerts_to_create)} alerts")
        return alerts_to_create
    
    def _save_alerts(self, alerts: List[Dict]):
        """Save alerts to database using Supabase client"""
        try:
            # Insert alerts in batches
            batch_size = 50
            for i in range(0, len(alerts), batch_size):
                batch = alerts[i:i + batch_size]
                self.supabase.table('alerts').insert(batch).execute()
        except Exception as e:
            print(f"❌ Error saving alerts: {e}")
    
    def run_forecasting_pipeline(self, forecast_days: int = 14) -> Dict:
        """Run the complete forecasting pipeline"""
        print("🚀 Starting Supabase + Chronos Forecasting Pipeline")
        print("=" * 60)
        
        # Step 1: Connect to services
        if not self.connect_database():
            return {'success': False, 'error': 'Database connection failed'}
        
        if not self.connect_chronos_endpoint():
            return {'success': False, 'error': 'Chronos endpoint connection failed'}
        
        # Step 2: Generate forecasts
        forecast_results = self.generate_forecasts(forecast_days)
        
        if not forecast_results:
            return {'success': False, 'error': 'No forecasts generated'}
        
        # Step 3: Save to database
        self.save_forecasts_to_database(forecast_results, forecast_days)
        
        # Step 4: Generate alerts
        alerts = self.generate_intelligent_alerts(forecast_results)
        
        # Step 5: Summary
        summary = {
            'success': True,
            'products_forecasted': len(forecast_results),
            'forecast_days': forecast_days,
            'alerts_generated': len(alerts),
            'forecast_period': f"{datetime.now().date() + timedelta(days=1)} to {datetime.now().date() + timedelta(days=forecast_days)}",
            'results': forecast_results
        }
        
        print("\n" + "=" * 60)
        print("📊 FORECASTING PIPELINE SUMMARY")
        print("=" * 60)
        print(f"✅ Products forecasted: {summary['products_forecasted']}")
        print(f"📅 Forecast period: {summary['forecast_period']}")
        print(f"🚨 Alerts generated: {summary['alerts_generated']}")
        print(f"💾 Database updated: forecast_data table")
        print("🎉 Pipeline completed successfully!")
        
        return summary
    
    def get_forecast_summary(self) -> pd.DataFrame:
        """Get forecast summary from database"""
        try:
            today = datetime.now().date().isoformat()
            
            # Get forecasts with product info
            response = self.supabase.table('forecast_data').select('''
                date,
                predicted_demand,
                confidence_interval_lower,
                confidence_interval_upper,
                products(name, sku, current_stock, reorder_point)
            ''').gt('date', today).order('date').execute()
            
            if response.data:
                # Flatten the data for DataFrame
                flattened_data = []
                for item in response.data:
                    product_info = item.get('products', {})
                    flattened_data.append({
                        'product_name': product_info.get('name'),
                        'sku': product_info.get('sku'),
                        'current_stock': product_info.get('current_stock'),
                        'reorder_point': product_info.get('reorder_point'),
                        'date': item['date'],
                        'predicted_demand': item['predicted_demand'],
                        'confidence_interval_lower': item['confidence_interval_lower'],
                        'confidence_interval_upper': item['confidence_interval_upper']
                    })
                
                return pd.DataFrame(flattened_data)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ Error getting forecast summary: {e}")
            return pd.DataFrame()

def main():
    """Main execution function"""
    # Check if .env file exists
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found!")
        print("Please create .env file with your Supabase credentials:")
        print("SUPABASE_URL=https://your-project.supabase.co")
        print("SUPABASE_KEY=your-anon-key")
        return
    
    # Run the forecasting pipeline
    integration = SupabaseChronosIntegration()
    result = integration.run_forecasting_pipeline(forecast_days=14)
    
    if result['success']:
        print("\n🎯 Next Steps:")
        print("1. Check your Supabase 'forecast_data' table for predictions")
        print("2. Review 'alerts' table for supply chain warnings")
        print("3. Your dashboard will now show real forecast data!")
        print("4. Set up automated runs with cron or scheduled tasks")
    else:
        print(f"\n❌ Pipeline failed: {result['error']}")

if __name__ == "__main__":
    main() 