#!/usr/bin/env python3
"""
Test JumpStart Chronos Endpoint
Test the deployed SageMaker JumpStart Chronos endpoint with supply chain data
"""

import json
import pandas as pd
from typing import Dict, List
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np

# SageMaker imports
from sagemaker.predictor import Predictor
from sagemaker.session import Session
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer

class JumpStartTester:
    def __init__(self):
        """Initialize tester for JumpStart endpoint"""
        self.session = Session()
        self.predictor = None
        
    def load_endpoint(self) -> bool:
        """Load endpoint from deployment info"""
        deployment_info_path = Path("deployment_info_jumpstart.json")
        
        if not deployment_info_path.exists():
            print("❌ No JumpStart deployment info found. Please deploy first.")
            return False
            
        with open(deployment_info_path, 'r') as f:
            info = json.load(f)
            
        endpoint_name = info.get("endpoint_name")
        if not endpoint_name:
            print("❌ No endpoint name found in deployment info.")
            return False
            
        print(f"Loading endpoint: {endpoint_name}")
        
        try:
            self.predictor = Predictor(
                endpoint_name=endpoint_name,
                serializer=JSONSerializer(),
                deserializer=JSONDeserializer(),
                sagemaker_session=self.session
            )
            print(f"✅ Endpoint loaded successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to load endpoint: {e}")
            return False
    
    def test_basic_forecast(self) -> Dict:
        """Test basic forecasting capability"""
        print("\n🧪 Testing basic forecasting...")
        
        payload = {
            "inputs": [
                {
                    "target": [100.0, 105.0, 98.0, 102.0, 110.0, 95.0, 103.0, 108.0, 99.0, 106.0],
                    "item_id": "basic_test",
                    "start": "2024-01-01T00:00:00"
                }
            ],
            "parameters": {
                "prediction_length": 5,
                "quantile_levels": [0.1, 0.5, 0.9],
                "freq": "D"
            }
        }
        
        try:
            response = self.predictor.predict(payload)
            print("✅ Basic forecast test passed!")
            
            prediction = response['predictions'][0]
            median_forecast = prediction['0.5']
            print(f"   5-day forecast (median): {[round(v, 1) for v in median_forecast]}")
            
            return response
        except Exception as e:
            print(f"❌ Basic forecast test failed: {e}")
            return None
    
    def test_supply_chain_scenarios(self) -> Dict:
        """Test various supply chain forecasting scenarios"""
        print("\n🏭 Testing supply chain scenarios...")
        
        # Generate realistic supply chain data
        scenarios = {
            "seasonal_demand": self._generate_seasonal_data(),
            "trending_growth": self._generate_trending_data(),
            "volatile_demand": self._generate_volatile_data(),
            "stable_inventory": self._generate_stable_data()
        }
        
        all_results = {}
        
        for scenario_name, time_series in scenarios.items():
            print(f"   Testing {scenario_name}...")
            
            payload = {
                "inputs": [
                    {
                        "target": time_series,
                        "item_id": scenario_name,
                        "start": "2024-01-01T00:00:00"
                    }
                ],
                "parameters": {
                    "prediction_length": 14,  # 2 weeks forecast
                    "quantile_levels": [0.1, 0.25, 0.5, 0.75, 0.9],
                    "freq": "D"
                }
            }
            
            try:
                response = self.predictor.predict(payload)
                prediction = response['predictions'][0]
                
                # Extract key metrics
                median_forecast = prediction['0.5']
                confidence_interval = {
                    'lower': prediction['0.1'],
                    'upper': prediction['0.9']
                }
                
                all_results[scenario_name] = {
                    'forecast': median_forecast,
                    'confidence': confidence_interval,
                    'status': 'success'
                }
                
                print(f"     ✅ {scenario_name}: 14-day forecast generated")
                print(f"        First 3 days: {[round(v, 1) for v in median_forecast[:3]]}")
                
            except Exception as e:
                print(f"     ❌ {scenario_name} failed: {e}")
                all_results[scenario_name] = {'status': 'failed', 'error': str(e)}
        
        return all_results
    
    def test_multi_product_batch(self) -> Dict:
        """Test batch forecasting for multiple products"""
        print("\n📦 Testing multi-product batch forecasting...")
        
        # Simulate multiple product demand patterns
        products = [
            {"id": "SKU_001_electronics", "demand": self._generate_electronics_demand()},
            {"id": "SKU_002_clothing", "demand": self._generate_clothing_demand()},
            {"id": "SKU_003_food", "demand": self._generate_food_demand()},
            {"id": "SKU_004_seasonal", "demand": self._generate_seasonal_demand()},
        ]
        
        payload = {
            "inputs": [
                {
                    "target": product["demand"],
                    "item_id": product["id"],
                    "start": "2024-01-01T00:00:00"
                }
                for product in products
            ],
            "parameters": {
                "prediction_length": 7,
                "quantile_levels": [0.1, 0.5, 0.9],
                "freq": "D",
                "batch_size": 4
            }
        }
        
        try:
            response = self.predictor.predict(payload)
            print(f"✅ Batch forecast completed for {len(products)} products!")
            
            results = {}
            for i, prediction in enumerate(response['predictions']):
                item_id = prediction['item_id']
                forecast = prediction['0.5']
                results[item_id] = forecast
                
                print(f"   📊 {item_id}")
                print(f"      7-day forecast: {[round(v, 1) for v in forecast]}")
            
            return results
            
        except Exception as e:
            print(f"❌ Batch forecasting failed: {e}")
            return None
    
    def test_covariates_forecasting(self) -> Dict:
        """Test forecasting with covariates (external features)"""
        print("\n🔗 Testing covariate-based forecasting...")
        
        # Historical data (30 days)
        target_demand = [45 + 5*np.sin(i/7) + np.random.normal(0, 2) for i in range(30)]
        
        # Past covariates (same length as target)
        promotional_activity = [1 if i % 7 in [5, 6] else 0 for i in range(30)]  # Weekend promos
        price_level = ["high" if i % 10 < 3 else "medium" if i % 10 < 7 else "low" for i in range(30)]
        
        # Future covariates (forecast horizon length)
        future_promos = [1, 1, 0, 0, 0, 1, 1]  # Next week promotion schedule
        future_prices = ["medium", "medium", "low", "low", "low", "high", "high"]
        
        payload = {
            "inputs": [
                {
                    "target": target_demand,
                    "item_id": "covariate_test_product",
                    "start": "2024-01-01T00:00:00",
                    "past_covariates": {
                        "promotion": promotional_activity,
                        "price_tier": price_level
                    },
                    "future_covariates": {
                        "promotion": future_promos,
                        "price_tier": future_prices
                    }
                }
            ],
            "parameters": {
                "prediction_length": 7,
                "quantile_levels": [0.1, 0.5, 0.9],
                "freq": "D",
                "covariate_model": "GBM"  # LightGBM for covariate modeling
            }
        }
        
        try:
            response = self.predictor.predict(payload)
            prediction = response['predictions'][0]
            
            print("✅ Covariate-based forecast successful!")
            print(f"   📈 7-day forecast with promotions/pricing:")
            
            forecast = prediction['0.5']
            for i, (day_forecast, promo, price) in enumerate(zip(forecast, future_promos, future_prices)):
                promo_indicator = "🎯" if promo else "  "
                print(f"      Day {i+1}: {day_forecast:.1f} units {promo_indicator} (price: {price})")
            
            return response
            
        except Exception as e:
            print(f"❌ Covariate forecasting failed: {e}")
            return None
    
    def _generate_seasonal_data(self) -> List[float]:
        """Generate seasonal demand pattern"""
        days = 60
        return [50 + 20*np.sin(2*np.pi*i/30) + np.random.normal(0, 5) for i in range(days)]
    
    def _generate_trending_data(self) -> List[float]:
        """Generate trending growth pattern"""
        days = 60
        return [30 + 0.5*i + np.random.normal(0, 3) for i in range(days)]
    
    def _generate_volatile_data(self) -> List[float]:
        """Generate volatile demand pattern"""
        days = 60
        return [100 + np.random.normal(0, 15) for i in range(days)]
    
    def _generate_stable_data(self) -> List[float]:
        """Generate stable inventory pattern"""
        days = 60
        return [75 + np.random.normal(0, 3) for i in range(days)]
    
    def _generate_electronics_demand(self) -> List[float]:
        """Electronics demand pattern - steady with occasional spikes"""
        days = 45
        base_demand = [25 + np.random.normal(0, 3) for i in range(days)]
        # Add some spikes (product launches, sales events)
        spike_days = [10, 25, 40]
        for day in spike_days:
            if day < len(base_demand):
                base_demand[day] += 30
        return base_demand
    
    def _generate_clothing_demand(self) -> List[float]:
        """Clothing demand - seasonal pattern"""
        days = 45
        return [40 + 15*np.sin(2*np.pi*i/90) + np.random.normal(0, 4) for i in range(days)]
    
    def _generate_food_demand(self) -> List[float]:
        """Food demand - consistent with weekly patterns"""
        days = 45
        weekly_pattern = [1.0, 0.8, 0.9, 0.9, 1.1, 1.3, 1.2]  # Mon-Sun multipliers
        return [60 * weekly_pattern[i % 7] + np.random.normal(0, 3) for i in range(days)]
    
    def _generate_seasonal_demand(self) -> List[float]:
        """Seasonal product demand"""
        days = 45
        return [20 + 30*max(0, np.sin(2*np.pi*i/365)) + np.random.normal(0, 2) for i in range(days)]
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting JumpStart Chronos Endpoint Test Suite")
        print("=" * 60)
        
        # Load endpoint
        if not self.load_endpoint():
            return
        
        test_results = {}
        
        # Run all tests
        test_results['basic'] = self.test_basic_forecast()
        test_results['supply_chain'] = self.test_supply_chain_scenarios()
        test_results['batch'] = self.test_multi_product_batch()
        test_results['covariates'] = self.test_covariates_forecasting()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUITE SUMMARY")
        print("=" * 60)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name.upper()}: {status}")
        
        successful_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        
        print(f"\nOverall: {successful_tests}/{total_tests} tests passed")
        
        if successful_tests == total_tests:
            print("🎉 All tests passed! JumpStart endpoint is ready for production.")
        else:
            print("⚠️  Some tests failed. Please check the endpoint configuration.")

def main():
    """Main test function"""
    tester = JumpStartTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 