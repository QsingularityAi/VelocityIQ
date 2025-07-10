#!/usr/bin/env python3
"""
Supply Chain Forecast Dashboard
View and analyze forecasting results from Supabase database
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class ForecastDashboard:
    def __init__(self):
        """Initialize dashboard with database connection"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        
    def connect(self) -> bool:
        """Connect to Supabase database"""
        try:
            # No explicit connection needed with the Supabase client
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def get_forecast_summary(self) -> pd.DataFrame:
        """Get comprehensive forecast summary"""
        today = datetime.now().date()
        try:
            # Get forecast data
            forecast_results = self.client.from_("forecast_data").select("""
                product_id,
                date,
                predicted_demand,
                confidence_interval_lower,
                confidence_interval_upper,
                created_at
            """).gte('date', today.isoformat()).execute().data
            
            if not forecast_results:
                return pd.DataFrame()
            
            # Get products data
            product_results = self.client.from_("products").select("""
                id,
                name,
                sku,
                category,
                current_stock,
                reorder_point,
                unit_cost,
                supplier_id
            """).execute().data
            
            # Get suppliers data
            supplier_results = self.client.from_("suppliers").select("""
                id,
                name,
                lead_time_days,
                reliability_score
            """).execute().data
            
            # Convert to DataFrames
            forecast_df = pd.DataFrame(forecast_results)
            product_df = pd.DataFrame(product_results) if product_results else pd.DataFrame()
            supplier_df = pd.DataFrame(supplier_results) if supplier_results else pd.DataFrame()
            
            # Merge data
            if not product_df.empty:
                df = forecast_df.merge(product_df, left_on='product_id', right_on='id', how='left')
                df = df.rename(columns={'name': 'product_name'})
                
                # Merge supplier data
                if not supplier_df.empty:
                    supplier_df = supplier_df.rename(columns={'name': 'supplier_name'})
                    df = df.merge(supplier_df, left_on='supplier_id', right_on='id', how='left', suffixes=('', '_supplier'))
                else:
                    df['supplier_name'] = 'Unknown'
                    df['lead_time_days'] = 0
                    df['reliability_score'] = 0
            else:
                df = forecast_df
                df['product_name'] = 'Unknown'
                df['sku'] = 'Unknown'
                df['category'] = 'Unknown'
                df['current_stock'] = 0
                df['reorder_point'] = 0
                df['unit_cost'] = 0
                df['supplier_name'] = 'Unknown'
                df['lead_time_days'] = 0
                df['reliability_score'] = 0
            
            # Clean up and format
            df = df.rename(columns={
                'date': 'forecast_date',
                'created_at': 'forecast_created'
            })
            
            if not df.empty:
                df['forecast_date'] = pd.to_datetime(df['forecast_date'], errors='coerce')
                df.dropna(subset=['forecast_date'], inplace=True)
                df['forecast_date'] = df['forecast_date'].dt.date
            
            # Select relevant columns
            columns = ['product_name', 'sku', 'category', 'current_stock', 'reorder_point', 
                      'unit_cost', 'supplier_name', 'lead_time_days', 'reliability_score',
                      'forecast_date', 'predicted_demand', 'confidence_interval_lower', 
                      'confidence_interval_upper', 'forecast_created']
            
            df = df[[col for col in columns if col in df.columns]]
            return df
            
        except Exception as e:
            print(f"❌ Error fetching forecast summary: {e}")
            return pd.DataFrame()
    
    def get_critical_alerts(self) -> pd.DataFrame:
        """Get current critical alerts"""
        try:
            # Get alerts data
            alerts_results = self.client.from_("alerts").select("""
                type,
                severity,
                title,
                description,
                created_at,
                product_id
            """).eq('is_resolved', False).order('created_at', desc=True).execute().data
            
            if not alerts_results:
                return pd.DataFrame()
            
            alerts_df = pd.DataFrame(alerts_results)
            
            # Get products and suppliers for context
            if 'product_id' in alerts_df.columns and alerts_df['product_id'].notna().any():
                product_ids = alerts_df['product_id'].dropna().unique()
                
                # Get products
                product_results = self.client.from_("products").select("""
                    id,
                    name,
                    sku,
                    supplier_id
                """).in_('id', product_ids.tolist()).execute().data
                
                if product_results:
                    product_df = pd.DataFrame(product_results)
                    product_df = product_df.rename(columns={'name': 'product_name'})
                    
                    # Get suppliers
                    supplier_ids = product_df['supplier_id'].dropna().unique()
                    if len(supplier_ids) > 0:
                        supplier_results = self.client.from_("suppliers").select("""
                            id,
                            name
                        """).in_('id', supplier_ids.tolist()).execute().data
                        
                        if supplier_results:
                            supplier_df = pd.DataFrame(supplier_results)
                            supplier_df = supplier_df.rename(columns={'name': 'supplier_name'})
                            
                            # Merge supplier info into products
                            product_df = product_df.merge(supplier_df, left_on='supplier_id', right_on='id', how='left', suffixes=('', '_supplier'))
                        else:
                            product_df['supplier_name'] = 'Unknown'
                    else:
                        product_df['supplier_name'] = 'Unknown'
                    
                    # Merge with alerts
                    alerts_df = alerts_df.merge(product_df[['id', 'product_name', 'sku', 'supplier_name']], 
                                              left_on='product_id', right_on='id', how='left', suffixes=('', '_product'))
                else:
                    alerts_df['product_name'] = 'Unknown'
                    alerts_df['sku'] = 'Unknown'
                    alerts_df['supplier_name'] = 'Unknown'
            else:
                alerts_df['product_name'] = 'Unknown'
                alerts_df['sku'] = 'Unknown'
                alerts_df['supplier_name'] = 'Unknown'
            
            # Sort by severity and created_at
            severity_order = {'critical': 1, 'high': 2, 'medium': 3, 'low': 4}
            alerts_df['severity_order'] = alerts_df['severity'].map(severity_order).fillna(5)
            alerts_df = alerts_df.sort_values(['severity_order', 'created_at'], ascending=[True, False])
            
            # Clean up columns
            final_columns = ['type', 'severity', 'title', 'description', 'created_at', 'product_name', 'sku', 'supplier_name']
            alerts_df = alerts_df[[col for col in final_columns if col in alerts_df.columns]]
            
            if not alerts_df.empty:
                alerts_df['created_at'] = pd.to_datetime(alerts_df['created_at'], errors='coerce')
                alerts_df.dropna(subset=['created_at'], inplace=True)
            
            return alerts_df
            
        except Exception as e:
            print(f"❌ Error fetching critical alerts: {e}")
            return pd.DataFrame()
    
    def get_stock_status(self) -> pd.DataFrame:
        """Get current stock status with days until stockout"""
        try:
            # Get basic product information with supplier details
            products_result = self.client.from_("products").select("""
                id,
                name,
                sku,
                current_stock,
                reorder_point,
                supplier_id,
                suppliers!inner(name, lead_time_days)
            """).execute().data
            
            if not products_result:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(products_result)
            
            # Flatten supplier data
            df['supplier_name'] = df['suppliers'].apply(lambda x: x['name'] if x else 'Unknown')
            df['lead_time_days'] = df['suppliers'].apply(lambda x: x['lead_time_days'] if x else 0)
            df = df.drop('suppliers', axis=1)
            df = df.rename(columns={'name': 'product_name'})
            
            # Get forecast data for next 7 days to calculate demand
            today = datetime.now().date()
            next_week = today + timedelta(days=7)
            
            forecast_result = self.client.from_("forecast_data").select("""
                product_id,
                predicted_demand
            """).gte('date', today.isoformat()).lte('date', next_week.isoformat()).execute().data
            
            # Calculate average daily demand for each product
            if forecast_result:
                forecast_df = pd.DataFrame(forecast_result)
                avg_demand = forecast_df.groupby('product_id')['predicted_demand'].mean().reset_index()
                avg_demand.columns = ['id', 'avg_daily_demand']
                
                # Merge with products
                df = df.merge(avg_demand, on='id', how='left')
            else:
                df['avg_daily_demand'] = 0
            
            # Calculate days until stockout and stock status
            df['avg_daily_demand'] = df['avg_daily_demand'].fillna(0)
            df['days_until_stockout'] = np.where(
                df['avg_daily_demand'] > 0,
                (df['current_stock'] / df['avg_daily_demand']).round(1),
                None
            )
            
            # Determine stock status
            def get_stock_status(row):
                if row['current_stock'] <= row['reorder_point']:
                    return 'REORDER NOW'
                elif row['avg_daily_demand'] > 0:
                    days_coverage = row['current_stock'] / row['avg_daily_demand']
                    if days_coverage <= 7:
                        return 'LOW STOCK'
                    elif days_coverage <= 14:
                        return 'MONITOR'
                return 'OK'
            
            df['stock_status'] = df.apply(get_stock_status, axis=1)
            
            # Clean up columns
            df = df[['product_name', 'sku', 'current_stock', 'reorder_point', 
                    'supplier_name', 'lead_time_days', 'days_until_stockout', 'stock_status']]
            
            return df
            
        except Exception as e:
            print(f"❌ Error fetching stock status: {e}")
            return pd.DataFrame()
    
    def get_demand_trends(self) -> pd.DataFrame:
        """Get demand trend analysis"""
        today = datetime.now().date()
        try:
            # Get forecast data
            forecast_results = self.client.from_("forecast_data").select("""
                product_id,
                date,
                predicted_demand
            """).gte('date', today.isoformat()).order('product_id', desc=False).order('date', desc=False).execute().data
            
            if not forecast_results:
                return pd.DataFrame()
            
            # Get products data
            product_results = self.client.from_("products").select("""
                id,
                name,
                sku,
                category
            """).execute().data
            
            # Convert to DataFrames
            forecast_df = pd.DataFrame(forecast_results)
            product_df = pd.DataFrame(product_results) if product_results else pd.DataFrame()
            
            # Merge with products
            if not product_df.empty:
                df = forecast_df.merge(product_df, left_on='product_id', right_on='id', how='left')
                df = df.rename(columns={'name': 'product_name'})
            else:
                df = forecast_df
                df['product_name'] = 'Unknown'
                df['sku'] = 'Unknown'
                df['category'] = 'Unknown'
            
            # Convert date and ensure proper sorting
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values(['product_id', 'date'])
            
            # Calculate trend metrics in Python
            df['predicted_demand'] = pd.to_numeric(df['predicted_demand'], errors='coerce')
            
            # Calculate 7-day lagged demand
            df['demand_7_days_ago'] = df.groupby('product_id')['predicted_demand'].shift(7)
            
            # Calculate 7-day rolling average
            df['rolling_7_day_avg'] = df.groupby('product_id')['predicted_demand'].rolling(
                window=7, min_periods=1
            ).mean().reset_index(level=0, drop=True)
            
            # Clean up columns
            final_columns = ['product_name', 'sku', 'category', 'date', 'predicted_demand', 
                           'demand_7_days_ago', 'rolling_7_day_avg']
            df = df[[col for col in final_columns if col in df.columns]]
            
            return df
            
        except Exception as e:
            print(f"❌ Error fetching demand trends: {e}")
            return pd.DataFrame()
    
    def display_dashboard(self):
        """Display comprehensive dashboard"""
        print("🏭 SUPPLY CHAIN FORECAST DASHBOARD")
        print("=" * 80)
        print(f"📅 Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. Critical Alerts
        print("🚨 CRITICAL ALERTS")
        print("-" * 40)
        alerts = self.get_critical_alerts()
        if alerts.empty:
            print("✅ No critical alerts")
        else:
            for _, alert in alerts.head(5).iterrows():
                severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(alert['severity'], "⚪")
                product_name = alert.get('product_name', 'N/A')
                sku = alert.get('sku', 'N/A')
                print(f"{severity_icon} {alert['title']}")
                print(f"   Product: {product_name} ({sku})")
                print(f"   {alert['description']}")
                print()
        
        # 2. Stock Status
        print("\n📦 STOCK STATUS OVERVIEW")
        print("-" * 40)
        stock_status = self.get_stock_status()
        
        status_counts = stock_status['stock_status'].value_counts()
        for status, count in status_counts.items():
            status_icon = {
                "REORDER NOW": "🔴",
                "LOW STOCK": "🟠", 
                "MONITOR": "🟡",
                "OK": "🟢"
            }.get(status, "⚪")
            print(f"{status_icon} {status}: {count} products")
        
        print("\nTop 5 Products Needing Attention:")
        critical_stock = stock_status[stock_status['stock_status'].isin(['REORDER NOW', 'LOW STOCK'])].head(5)
        
        if critical_stock.empty:
            print("✅ All products have adequate stock levels")
        else:
            for _, product in critical_stock.iterrows():
                print(f"📦 {product['product_name']} ({product['sku']})")
                print(f"   Stock: {product['current_stock']} units | Reorder Point: {product['reorder_point']}")
                if product['days_until_stockout']:
                    print(f"   Days until stockout: {product['days_until_stockout']}")
                print(f"   Supplier: {product['supplier_name']} (Lead time: {product['lead_time_days']} days)")
                print()
        
        # 3. Forecast Summary
        print("\n🔮 FORECAST SUMMARY (Next 7 Days)")
        print("-" * 40)
        forecasts = self.get_forecast_summary()
        
        if forecasts.empty:
            print("❌ No forecast data available. Run forecasting pipeline first.")
        else:
            next_week = forecasts[
                forecasts['forecast_date'] <= (datetime.now().date() + timedelta(days=7))
            ]
            
            summary_stats = next_week.groupby('product_name').agg({
                'predicted_demand': ['sum', 'mean', 'std'],
                'current_stock': 'first'
            }).round(2)
            
            summary_stats.columns = ['Total_Demand', 'Avg_Daily_Demand', 'Demand_Volatility', 'Current_Stock']
            summary_stats['Stock_Coverage_Days'] = (
                summary_stats['Current_Stock'] / summary_stats['Avg_Daily_Demand']
            ).round(1)
            
            print("Product Performance (7-day outlook):")
            for product_name, stats in summary_stats.head(10).iterrows():
                coverage = stats['Stock_Coverage_Days']
                coverage_icon = "🔴" if coverage <= 3 else "🟠" if coverage <= 7 else "🟢"
                
                print(f"{coverage_icon} {product_name}")
                print(f"   Expected demand: {stats['Total_Demand']:.1f} units (avg: {stats['Avg_Daily_Demand']:.1f}/day)")
                print(f"   Current stock: {stats['Current_Stock']:.0f} units ({coverage:.1f} days coverage)")
                print()
        
        # 4. Demand Trends
        print("\n📈 DEMAND TRENDS")
        print("-" * 40)
        trends = self.get_demand_trends()
        
        if not trends.empty:
            # Calculate trend indicators
            recent_trends = trends.dropna().copy()
            recent_trends['demand_change_pct'] = (
                (recent_trends['predicted_demand'] - recent_trends['demand_7_days_ago']) / 
                recent_trends['demand_7_days_ago'] * 100
            ).round(1)
            
            # Get products with significant trends
            trending_products = recent_trends[
                abs(recent_trends['demand_change_pct']) >= 15  # 15% change threshold
            ].groupby('product_name')['demand_change_pct'].mean().sort_values(ascending=False)
            
            if trending_products.empty:
                print("📊 No significant demand trends detected")
            else:
                print("Significant demand changes (vs. 7 days ago):")
                for product, change in trending_products.head(5).items():
                    trend_icon = "📈" if change > 0 else "📉"
                    print(f"{trend_icon} {product}: {change:+.1f}% change")
        
        print("\n" + "=" * 80)
        print("🎯 Dashboard completed. For detailed analysis, check Supabase tables:")
        print("   • forecast_data - Detailed predictions")
        print("   • alerts - Action items")
        print("   • products - Current inventory levels")
    
    def export_forecast_report(self, filename: str = None):
        """Export detailed forecast report to CSV"""
        if filename is None:
            filename = f"forecast_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        forecasts = self.get_forecast_summary()
        forecasts.to_csv(filename, index=False)
        print(f"📄 Forecast report exported to: {filename}")
        return filename
    
    def __del__(self):
        """Clean up database connection"""
        pass

def main():
    """Main dashboard function"""
    dashboard = ForecastDashboard()
    
    if not dashboard.connect():
        print("❌ Cannot connect to database. Please check your .env file.")
        return
    
    try:
        dashboard.display_dashboard()
        
        # Ask if user wants to export report
        export = input("\n📄 Export detailed forecast report to CSV? (y/n): ").lower().strip()
        if export in ['y', 'yes']:
            filename = dashboard.export_forecast_report()
            print(f"✅ Report saved as {filename}")
            
    except Exception as e:
        print(f"❌ Dashboard error: {e}")

if __name__ == "__main__":
    main()
