# 🏭 VelocityIQ: AI-Powered Supply Chain Forecasting Platform

**A complete end-to-end supply chain forecasting solution with interactive dashboard, powered by Amazon Chronos-Bolt models and real-time Supabase integration.**

![VelocityIQ Platform](https://via.placeholder.com/800x300/3B82F6/FFFFFF?text=VelocityIQ+Supply+Chain+Platform)

## 🚀 Platform Overview

VelocityIQ provides a comprehensive supply chain forecasting platform that combines:

- **🤖 AI-Powered Forecasting**: Custom Chronos-Bolt models fine-tuned on your data
- **📊 Interactive Dashboard**: Modern React-based real-time analytics interface  
- **☁️ Multiple Deployment Options**: Custom training or AWS JumpStart deployment
- **🔄 Real-time Integration**: Live Supabase database connectivity
- **🚨 Intelligent Alerts**: Automated supply chain risk detection
- **📈 Business Intelligence**: Advanced analytics and trend visualization

## 🏗️ System Architecture

```
VelocityIQ Platform
├── 📊 Interactive Dashboard (React + Tailwind)
│   ├── Real-time forecasting charts
│   ├── Inventory management interface
│   ├── Alert management system
│   └── Business intelligence analytics
├── 🔥 FastAPI Backend
│   ├── RESTful API endpoints
│   ├── Real-time data processing
│   └── Database connectivity
├── 🤖 AI/ML Engine
│   ├── Custom Chronos-Bolt models
│   ├── AWS SageMaker deployment
│   └── JumpStart pre-built models
└── 🗄️ Supabase Database
    ├── Supply chain data management
    ├── Real-time forecasting storage
    └── Alert and notification system
```

## 🎯 Quick Start

### 🚀 Option 1: One-Command Dashboard Launch (Recommended)

```bash
# 1. Install dependencies
pip install -r requirements_dashboard.txt

# 2. Set up environment (.env file required)
# SUPABASE_URL=your_supabase_project_url
# SUPABASE_ANON_KEY=your_supabase_anon_key

# 3. Deploy database schema
# Run supabase-schema.sql in your Supabase SQL editor

# 4. Launch the complete platform
python start_dashboard.py
```

**Access Points:**
- 🖥️ **Dashboard UI**: http://localhost:3000
- 📊 **API Server**: http://localhost:8000  
- 📚 **API Documentation**: http://localhost:8000/docs

### ⚡ Option 2: JumpStart Deployment (Production-Ready)

```bash
# 1. Set up AWS SageMaker role
python create_sagemaker_role.py

# 2. Deploy pre-trained Chronos model
python deploy_jumpstart_chronos.py

# 3. Run integrated forecasting pipeline
python supabase_forecasting_integration.py

# 4. Launch dashboard
python start_dashboard.py
```

## 📋 Prerequisites

### Required Software
- **Python 3.9+** with pip
- **Node.js 16+** with npm (auto-installed for dashboard)
- **AWS CLI** configured with appropriate permissions

### AWS Requirements
- AWS Account with SageMaker access
- IAM role with SageMaker permissions (created automatically)
- S3 bucket access for model storage

### Database Requirements
- **Supabase Project** with provided schema deployed
- API keys and project URL configured in `.env`

## 🛠️ Installation & Setup

### 1. Environment Configuration

Create a `.env` file in your project root:

```bash
# Supabase Configuration (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# AWS Configuration (Optional - can use AWS CLI)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1

# Dashboard Configuration (Optional)
SUPABASE_HOST=db.your-project.supabase.co
SUPABASE_DB=postgres
SUPABASE_USER=postgres
SUPABASE_PASSWORD=your_db_password
SUPABASE_PORT=5432
```

### 2. Database Schema Deployment

Deploy the provided schema to your Supabase project:

```bash
# Run this SQL file in your Supabase SQL editor
supabase-schema.sql
```

### 3. Dependency Installation

```bash
# Core dependencies
pip install -r requirements.txt

# Dashboard-specific dependencies
pip install -r requirements_dashboard.txt

# JumpStart deployment dependencies
pip install -r requirements_jumpstart.txt

# Integration dependencies
pip install -r requirements_integration.txt
```

## 🔄 Usage Workflows

### 📊 Dashboard-First Workflow (Recommended for Business Users)

```bash
# Launch the complete platform
python start_dashboard.py

# Navigate to http://localhost:3000 for:
# - Real-time supply chain analytics
# - Interactive forecasting charts
# - Alert management interface
# - Inventory status monitoring
```

### 🤖 AI Model Deployment Workflows

#### AWS JumpStart (Easiest)
```bash
# 1. Create SageMaker execution role
python create_sagemaker_role.py

# 2. Deploy pre-trained Chronos model
python deploy_jumpstart_chronos.py

# 3. test_jumpstart integration
python test_jumpstart_endpoint.py

# 4. Run forecasting integration
python supabase_forecasting_integration.py
```


## 📱 Dashboard Features

### 🏠 Overview Dashboard
- **KPI Cards**: Revenue, orders, inventory levels, forecast accuracy
- **Demand Forecasting Charts**: Interactive time series with confidence intervals
- **Alert Summary**: Critical supply chain notifications
- **Trend Analysis**: Significant demand pattern detection

### 🚨 Alert Management
- **Severity Filtering**: Critical, high, medium, low priority alerts
- **Real-time Notifications**: Live alert system with auto-refresh
- **Product Context**: Direct links to affected inventory items
- **Action Recommendations**: AI-generated next steps

### 📦 Inventory Management
- **Live Stock Status**: Real-time inventory levels across all products
- **Search & Filtering**: Advanced product discovery and filtering
- **Supplier Analytics**: Lead times, reliability scores, cost analysis
- **Reorder Recommendations**: AI-powered restocking suggestions

### 📈 Forecasting Analytics
- **Multi-horizon Forecasts**: 7, 14, 30-day prediction views
- **Confidence Intervals**: Uncertainty quantification and risk assessment
- **Product Comparison**: Side-by-side forecast analysis
- **Historical Accuracy**: Model performance tracking and validation

## 🔧 Configuration Options

### 🤖 Model Configuration

**JumpStart Models** (Recommended):
```python
# Available pre-trained models
models = {
    "small": "autogluon-forecasting-chronos-bolt-small",    # Cost-effective
    "base": "autogluon-forecasting-chronos-bolt-base"      # Higher accuracy
}

# Instance types
instances = {
    "cost_optimized": "ml.c5.xlarge",      # ~$0.10/hour
    "performance": "ml.c5.2xlarge"         # ~$0.20/hour
}
```

**Custom Training**:
```python
config = {
    'model_name': 'amazon/chronos-bolt-small',
    'num_epochs': 5,
    'learning_rate': 5e-5,
    'batch_size': 4,
    'validation_split': 0.2
}
```

### 📊 Dashboard Configuration

```python
# API refresh intervals
DASHBOARD_REFRESH_INTERVAL = 30  # seconds
ALERT_CHECK_INTERVAL = 10       # seconds

# Chart configuration
FORECAST_PERIODS = [7, 14, 30]  # days
CONFIDENCE_LEVELS = [0.1, 0.9] # 80% confidence interval
```

### 🔄 Integration Configuration

```python
# Forecasting pipeline settings
PREDICTION_LENGTH = 14          # days to forecast
HISTORICAL_WINDOW = 90          # days of historical data
BATCH_SIZE = 32                # products per batch
```

## 📊 Understanding Results

### 📈 Forecast Outputs
- **Median Prediction**: Most likely demand scenario
- **Confidence Intervals**: 10th, 25th, 75th, 90th percentiles
- **Uncertainty Quantification**: Risk assessment for planning
- **Trend Indicators**: Direction and momentum analysis

### 🚨 Alert Types
1. **Stock Low**: Inventory below reorder point or predicted stockout
2. **Demand Spike**: Significant increase in predicted demand
3. **Supplier Risk**: Lead time or reliability issues
4. **Forecast Drift**: Model accuracy degradation alerts

### 📊 Business Intelligence
- **Demand Patterns**: Seasonal, trend, and cyclical analysis
- **Inventory Optimization**: Optimal stock level recommendations  
- **Cost Analysis**: Carrying costs vs. stockout risk
- **Performance Metrics**: Forecast accuracy and inventory turnover

## 🔍 API Reference

### 📡 Dashboard API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/dashboard/overview` | GET | KPI metrics and summary stats |
| `/api/dashboard/alerts` | GET | Current alerts with filtering |
| `/api/dashboard/stock-status` | GET | Real-time inventory levels |
| `/api/dashboard/forecasts` | GET | Forecast data with confidence intervals |
| `/api/dashboard/demand-trends` | GET | Trend analysis and patterns |
| `/api/dashboard/chart-data/{sku}` | GET | Product-specific time series |

### 🤖 ML Pipeline API

```python
# JumpStart Integration
from supabase_forecasting_integration import SupabaseChronosIntegration

integration = SupabaseChronosIntegration()
results = integration.run_forecasting_pipeline(forecast_days=14)

# Custom Model Training  
from train_chronos_custom import SupplyChainChronosTrainer

trainer = SupplyChainChronosTrainer()
model = trainer.train_model(training_data)

# Deployment
from deploy_jumpstart_chronos import JumpStartChronosDeployer

deployer = JumpStartChronosDeployer()
predictor = deployer.deploy_model()
```

## 🔧 Troubleshooting

### 🐛 Common Issues

**Dashboard Won't Start**
```bash
# Check Node.js installation
node --version && npm --version

# Clear npm cache if needed
cd dashboard && rm -rf node_modules && npm install

# Verify environment variables
python -c "import os; print(os.getenv('SUPABASE_URL'))"
```

**API Connection Failed**
```bash
# Test Supabase connection
python check_supabase_schema.py

# Verify API server
curl http://localhost:8000/api/dashboard/overview
```

**Model Deployment Issues**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify SageMaker role
python -c "
import json
with open('sagemaker_role.json') as f:
    print(json.load(f)['role_arn'])
"
```

**Database Connection Problems**
```bash
# Test database schema
python setup_supabase_schema.py

# Check table structure
python test_supabase_api.py
```

### ⚡ Performance Optimization

**Dashboard Performance**:
- Enable production build: `cd dashboard && npm run build`
- Use caching for API responses
- Implement data pagination for large datasets
- Optimize chart rendering with data sampling

**Model Performance**:
- Use appropriate instance types for your volume
- Implement request batching for multiple products
- Cache frequent predictions
- Monitor endpoint utilization and auto-scaling

## 🚀 Production Deployment

### 🌐 Dashboard Deployment
```bash
# Build React app for production
cd dashboard && npm run build

# Deploy using your preferred hosting (Vercel, Netlify, etc.)
# Static files will be in dashboard/build/
```

### ☁️ AWS Infrastructure
```bash
# Set up production-grade SageMaker endpoints
python deploy_jumpstart_chronos.py --instance-type ml.c5.2xlarge

# Configure auto-scaling policies
# Set up CloudWatch monitoring
# Implement proper IAM security
```

### 🔒 Security & Compliance
- Use Supabase Row Level Security (RLS) policies
- Implement proper API authentication
- Set up AWS IAM least-privilege access
- Enable CloudTrail logging for audit trails
- Use environment-specific configurations

## 📚 Advanced Features

### 🔄 Automated Workflows
```bash
# Set up scheduled forecasting runs
# Linux/Mac crontab example:
0 2 * * * cd /path/to/velocityiq && python supabase_forecasting_integration.py

# AWS EventBridge for cloud automation
# GitHub Actions for CI/CD workflows
```

### 📊 Custom Analytics
- Extend dashboard with custom KPIs
- Implement additional alert types
- Add supplier performance metrics
- Create custom forecast accuracy reports

### 🔌 Integration Extensions
- Connect to ERP systems (SAP, Oracle)
- Integrate with inventory management platforms
- Add external data sources (weather, events)
- Implement real-time streaming data

## 🤝 Contributing

To extend VelocityIQ:

1. **Dashboard Components**: Add new React components in `dashboard/src/components/`
2. **API Endpoints**: Extend FastAPI routes in `dashboard_api.py`
3. **ML Models**: Add custom model types in training scripts
4. **Integrations**: Create new data connectors and pipelines
5. **Alerts**: Implement custom business rules and notification types

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 🆘 Support & Documentation

### 📖 Additional Documentation
- **Dashboard Guide**: See `DASHBOARD_README.md` for detailed dashboard documentation
- **API Documentation**: Visit http://localhost:8000/docs when running
- **Model Training**: Comprehensive guides in individual script files

### 🔍 Getting Help
1. Check the troubleshooting section above
2. Review component-specific README files
3. Examine deployment logs and error messages
4. Verify all prerequisites are properly configured

### 🌟 What's New in VelocityIQ

**Latest Features**:
- ✨ Modern React dashboard with real-time updates
- 🚀 One-command deployment with `start_dashboard.py`
- 🤖 AWS JumpStart integration for instant model deployment
- 🔄 Live Supabase integration with automatic data sync
- 🚨 Intelligent alert system with business rule engine
- 📊 Advanced business intelligence and analytics
- 📱 Mobile-responsive design for on-the-go access

---

## 🎯 Quick Commands Reference

```bash
# Complete Platform Setup
pip install -r requirements_dashboard.txt
python start_dashboard.py                    # 🖥️  http://localhost:3000

# AI Model Deployment  
python deploy_jumpstart_chronos.py          # 🤖 Deploy pre-trained model
python supabase_forecasting_integration.py  # 🔄 Run forecasting pipeline

# Development & Testing
python test_supabase_api.py                 # 🧪 Test database connection
python check_supabase_schema.py             # ✅ Verify schema setup
python test_jumpstart_endpoint.py           # 🔬 Test model endpoint

# Database Setup
# Run supabase-schema.sql in Supabase SQL editor
python setup_supabase_schema.py             # 🗄️  Initialize database

```

**🎉 Happy forecasting with VelocityIQ!** 

Transform your supply chain with AI-powered predictions and real-time business intelligence. 📈🏭