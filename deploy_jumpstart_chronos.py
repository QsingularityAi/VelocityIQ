#!/usr/bin/env python3
"""
SageMaker JumpStart Chronos Deployment
Deploy Chronos models using the official AWS JumpStart approach
Based on the official AWS Chronos deployment notebook
"""

import json
import boto3
import sagemaker
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import warnings
warnings.filterwarnings('ignore')

from dotenv import load_dotenv
load_dotenv()

from sagemaker.jumpstart.model import JumpStartModel
from sagemaker.predictor import Predictor
from pprint import pformat

class JumpStartChronosDeployer:
    def __init__(self, 
                 role: Optional[str] = None,
                 region: str = "us-east-1"):
        """
        Initialize JumpStart deployer for Chronos models
        
        Args:
            role: SageMaker execution role ARN
            region: AWS region for deployment
        """
        self.region = region
        
        # Initialize SageMaker session
        self.session = sagemaker.Session()
        self.bucket = self.session.default_bucket()
        
        # Get or create IAM role
        if role is None:
            self.role = sagemaker.get_execution_role()
        else:
            self.role = role
            
        print(f"Using SageMaker role: {self.role}")
        print(f"Using S3 bucket: {self.bucket}")
        print(f"Region: {self.region}")
    
    def cleanup_previous_deployment(self):
        """Deletes the previously deployed SageMaker endpoint if it exists."""
        deployment_info_path = Path("deployment_info_jumpstart.json")
        if not deployment_info_path.exists():
            print("No previous JumpStart deployment information found. Skipping cleanup.")
            return

        print("Found previous JumpStart deployment information. Attempting to clean up...")
        with open(deployment_info_path, 'r') as f:
            try:
                info = json.load(f)
                endpoint_name = info.get("endpoint_name")
                if endpoint_name:
                    print(f"Deleting old endpoint: {endpoint_name}")
                    try:
                        self.session.delete_endpoint(endpoint_name)
                        print(f"Waiting for endpoint {endpoint_name} to be deleted...")
                        waiter = self.session.sagemaker_client.get_waiter('endpoint_deleted')
                        waiter.wait(EndpointName=endpoint_name)
                        print(f"✅ Endpoint {endpoint_name} deleted successfully.")
                    except Exception as e:
                        if "Endpoint was not found" in str(e) or "ValidationException" in str(e):
                            print(f"Endpoint {endpoint_name} not found. It might have been deleted already.")
                        else:
                            print(f"⚠️  Could not delete endpoint {endpoint_name}: {e}")
                            print("Continuing with deployment, but you may need to clean up old endpoints manually.")
                else:
                    print("No endpoint name found in deployment_info_jumpstart.json.")
            except json.JSONDecodeError:
                print("Could not read deployment_info_jumpstart.json. Skipping cleanup.")

        # Clean up the old info file
        import os
        os.remove(deployment_info_path)
    
    def deploy_model(self, 
                    model_id: str = "autogluon-forecasting-chronos-bolt-small",
                    instance_type: str = "ml.c5.2xlarge",
                    endpoint_name: Optional[str] = None) -> Predictor:
        """
        Deploy Chronos model using SageMaker JumpStart
        
        Args:
            model_id: JumpStart model ID. Options:
                - autogluon-forecasting-chronos-bolt-base (larger, more accurate)
                - autogluon-forecasting-chronos-bolt-small (smaller, faster)
                - autogluon-forecasting-chronos-t5-small (original, requires GPU)
            instance_type: AWS instance type
            endpoint_name: Custom endpoint name (optional)
        """
        print("Deploying Chronos model using SageMaker JumpStart...")
        print(f"Model ID: {model_id}")
        print(f"Instance Type: {instance_type}")
        
        # Create JumpStart model
        model = JumpStartModel(
            model_id=model_id,
            instance_type=instance_type,
            role=self.role
        )
        
        # Deploy to endpoint
        print("Starting deployment... This may take 5-10 minutes.")
        predictor = model.deploy(endpoint_name=endpoint_name)
        
        print(f"✅ Model deployed successfully!")
        print(f"Endpoint name: {predictor.endpoint_name}")
        print(f"Instance type: {instance_type}")
        
        # Save deployment info
        deployment_info = {
            "endpoint_name": predictor.endpoint_name,
            "model_id": model_id,
            "instance_type": instance_type,
            "deployment_time": datetime.now().isoformat(),
            "region": self.region,
            "role": self.role,
            "deployment_type": "jumpstart"
        }
        
        with open("deployment_info_jumpstart.json", 'w') as f:
            json.dump(deployment_info, f, indent=2)
        
        return predictor
    
    def test_endpoint(self, predictor: Predictor) -> Dict:
        """Test the deployed endpoint with sample supply chain data"""
        print("Testing JumpStart endpoint...")
        
        # Test with supply chain style data
        test_payload = {
            "inputs": [
                {
                    "target": [45.0, 42.0, 48.0, 51.0, 47.0, 43.0, 46.0, 49.0, 52.0, 48.0, 44.0, 47.0, 50.0, 46.0, 42.0],
                    "item_id": "product_A_demand",
                    "start": "2024-01-01T00:00:00"
                },
                {
                    "target": [120.0, 115.0, 125.0, 130.0, 118.0, 122.0, 127.0, 124.0, 119.0, 126.0, 128.0, 123.0, 121.0, 125.0],
                    "item_id": "product_B_demand",
                    "start": "2024-01-01T00:00:00"
                }
            ],
            "parameters": {
                "prediction_length": 7,
                "quantile_levels": [0.1, 0.5, 0.9],
                "freq": "D"
            }
        }
        
        try:
            response = predictor.predict(test_payload)
            print("✅ Endpoint test successful!")
            
            if 'predictions' in response:
                print(f"Generated forecasts for {len(response['predictions'])} time series")
                
                for i, prediction in enumerate(response['predictions']):
                    item_id = prediction.get('item_id', f'series_{i+1}')
                    forecast_values = prediction.get('0.5', prediction.get('mean', []))
                    
                    print(f"  [{i+1}] {item_id}:")
                    print(f"      7-day forecast: {[round(v, 2) for v in forecast_values[:3]]}... (showing first 3)")
                    print(f"      Quantiles available: {[k for k in prediction.keys() if k.replace('.', '').isdigit()]}")
            
            return response
            
        except Exception as e:
            print(f"❌ Endpoint test failed: {e}")
            return None
    
    def nested_round(self, data, decimals=2):
        """Round numbers, including nested dicts and lists."""
        if isinstance(data, float):
            return round(data, decimals)
        elif isinstance(data, list):
            return [self.nested_round(item, decimals) for item in data]
        elif isinstance(data, dict):
            return {key: self.nested_round(value, decimals) for key, value in data.items()}
        else:
            return data

    def pretty_format(self, data):
        """Pretty format response data"""
        return pformat(self.nested_round(data), width=150, sort_dicts=False)

def main():
    """Main deployment function"""
    print("=" * 60)
    print("SAGEMAKER JUMPSTART CHRONOS DEPLOYMENT")
    print("=" * 60)
    print("Using the official AWS approach for Chronos model deployment")
    print("Benefits: Pre-built containers, optimized performance, AWS support")
    print()
    
    # Available models
    available_models = {
        "small": {
            "id": "autogluon-forecasting-chronos-bolt-small",
            "description": "Chronos-Bolt Small (48M params) - Fast and cost-effective",
            "recommended_instance": "ml.c5.xlarge"
        },
        "base": {
            "id": "autogluon-forecasting-chronos-bolt-base", 
            "description": "Chronos-Bolt Base (205M params) - More accurate",
            "recommended_instance": "ml.c5.2xlarge"
        }
    }
    
    # Configuration - using the smaller model for cost efficiency
    config = {
        'model_size': 'small',  # or 'base' for higher accuracy
        'instance_type': 'ml.c5.xlarge',  # Cost-effective CPU instance
        'endpoint_name': None  # Will be auto-generated
    }
    
    selected_model = available_models[config['model_size']]
    
    print("Deployment Configuration:")
    print(f"  Model: {selected_model['description']}")
    print(f"  Model ID: {selected_model['id']}")
    print(f"  Instance Type: {config['instance_type']}")
    print(f"  Estimated Cost: ~$0.10-0.20/hour")
    print()
    
    try:
        # Initialize deployer
        with open("sagemaker_role.json", "r") as f:
            role_config = json.load(f)
        deployer = JumpStartChronosDeployer(role=role_config['role_arn'])
        
        # Clean up previous deployment
        deployer.cleanup_previous_deployment()
        
        # Deploy model using JumpStart
        predictor = deployer.deploy_model(
            model_id=selected_model['id'],
            instance_type=config['instance_type'],
            endpoint_name=config['endpoint_name']
        )
        
        # Test endpoint
        test_result = deployer.test_endpoint(predictor)
        
        if test_result:
            print("\n" + "=" * 60)
            print("🎉 JUMPSTART DEPLOYMENT SUCCESSFUL!")
            print("=" * 60)
            print(f"Endpoint name: {predictor.endpoint_name}")
            print(f"Model: {selected_model['description']}")
            print(f"Instance: {config['instance_type']}")
            print(f"Ready for production supply chain forecasting!")
            print()
            print("Usage example:")
            print("```python")
            print("payload = {")
            print('    "inputs": [{"target": [your_demand_data], "item_id": "product_001"}],')
            print('    "parameters": {"prediction_length": 7}')
            print("}")
            print("forecast = predictor.predict(payload)")
            print("```")
            print()
            print("⚠️  Remember to delete the endpoint when done:")
            print(f"   predictor.delete_endpoint()")
        else:
            print("❌ Deployment completed but endpoint test failed")
            
    except FileNotFoundError:
        print("❌ sagemaker_role.json not found. Please create this file with your SageMaker role.")
        print("Example content:")
        print('{"role_arn": "arn:aws:iam::YOUR-ACCOUNT:role/YourSageMakerRole"}')
    except Exception as e:
        import traceback
        print(f"❌ Deployment failed: {e}")
        print("Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    main() 