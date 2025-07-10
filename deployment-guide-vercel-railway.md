# 🚀 VelocityIQ Deployment Guide: Vercel + Railway

## **Option 1: Serverless Deployment (Recommended for MVP)**

### **Architecture Overview**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vercel        │    │    Railway      │    │   Supabase      │
│   (Frontend)    │───▶│   (Backend)     │───▶│   (Database)    │
│   React App     │    │   FastAPI       │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  AWS SageMaker  │
                       │  (Chronos ML)   │
                       └─────────────────┘
```

---

## 📱 **Step 1: Frontend Deployment (Vercel)**

### **1.1 Prepare Frontend for Production**

Create `dashboard/next.config.js`:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  env: {
    REACT_APP_API_URL: process.env.REACT_APP_API_URL || 'https://your-railway-app.railway.app'
  }
}

module.exports = nextConfig
```

### **1.2 Update package.json Scripts**
```json
{
  "scripts": {
    "build": "react-scripts build",
    "build:vercel": "npm run build && cp -r build/* ./",
    "start": "react-scripts start"
  }
}
```

### **1.3 Create vercel.json**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "dashboard/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/dashboard/$1"
    }
  ],
  "env": {
    "REACT_APP_API_URL": "https://your-railway-backend.railway.app"
  }
}
```

### **1.4 Deploy to Vercel**
```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to project root
cd VelocityIQ

# Deploy frontend
vercel --prod

# Follow prompts:
# - Project name: velocityiq-dashboard
# - Framework: React
# - Build command: cd dashboard && npm run build
# - Output directory: dashboard/build
```

---

## 🔥 **Step 2: Backend Deployment (Railway)**

### **2.1 Prepare Backend for Railway**

Create `railway.json`:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn dashboard_api_fixed:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/",
    "healthcheckTimeout": 300
  }
}
```

Create `Procfile`:
```
web: uvicorn dashboard_api_fixed:app --host 0.0.0.0 --port $PORT
```

Create `runtime.txt`:
```
python-3.9.18
```

### **2.2 Update requirements.txt**
```txt
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
python-dotenv>=1.0.0
pandas>=2.0.0
numpy>=1.24.0
psycopg2-binary>=2.9.9
supabase>=2.3.0
boto3>=1.34.0
sagemaker>=2.200.0
httpx>=0.25.2
pydantic>=2.5.0
```

### **2.3 Update CORS for Production**

Update `dashboard_api_fixed.py`:
```python
# Enable CORS for production domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://your-vercel-domain.vercel.app",  # Add your Vercel domain
        "https://velocityiq-dashboard.vercel.app"  # Example
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **2.4 Deploy to Railway**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Set environment variables
railway variables set SUPABASE_URL=your_supabase_url
railway variables set SUPABASE_KEY=your_supabase_key
railway variables set AWS_ACCESS_KEY_ID=your_aws_key
railway variables set AWS_SECRET_ACCESS_KEY=your_aws_secret
railway variables set AWS_DEFAULT_REGION=us-east-1

# Deploy
railway up
```

---

## 🔧 **Step 3: Environment Configuration**

### **3.1 Update Frontend Environment**

Update `dashboard/src/services/apiService.js`:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 
  process.env.NODE_ENV === 'production' 
    ? 'https://your-railway-app.railway.app'
    : 'http://localhost:8000';
```

### **3.2 Set Production Environment Variables**

**Vercel Environment Variables:**
```bash
vercel env add REACT_APP_API_URL
# Enter: https://your-railway-app.railway.app
```

**Railway Environment Variables:**
```bash
railway variables set SUPABASE_URL=https://your-project.supabase.co
railway variables set SUPABASE_KEY=your_anon_key
railway variables set AWS_ACCESS_KEY_ID=your_aws_access_key
railway variables set AWS_SECRET_ACCESS_KEY=your_aws_secret_key
railway variables set AWS_DEFAULT_REGION=us-east-1
```

---

## 🔍 **Step 4: Testing Deployment**

### **4.1 Test Backend Health**
```bash
curl https://your-railway-app.railway.app/
curl https://your-railway-app.railway.app/api/dashboard/overview
```

### **4.2 Test Frontend**
```bash
# Visit your Vercel URL
https://your-vercel-domain.vercel.app
```

### **4.3 End-to-End Testing**
```python
import requests

# Test API endpoints
base_url = "https://your-railway-app.railway.app"
endpoints = [
    "/api/dashboard/overview",
    "/api/dashboard/alerts",
    "/api/dashboard/stock-status",
    "/api/dashboard/forecasts"
]

for endpoint in endpoints:
    response = requests.get(f"{base_url}{endpoint}")
    print(f"{endpoint}: {response.status_code}")
```

---

## 💰 **Cost Estimation**

### **Monthly Costs (Approximate)**
- **Vercel Pro**: $20/month (unlimited static sites)
- **Railway Hobby**: $5/month (512MB RAM, $5 usage)
- **Supabase**: Free tier (up to 500MB storage)
- **AWS SageMaker**: ~$20-50/month (depending on usage)

**Total: ~$45-75/month**

---

## 🔄 **CI/CD Setup**

### **Automatic Deployments**

**For Vercel (Frontend):**
- Connect your GitHub repository
- Auto-deploys on push to `main` branch
- Preview deployments for PRs

**For Railway (Backend):**
- Connect your GitHub repository
- Auto-deploys on push to `main` branch
- Environment-specific deployments

### **GitHub Actions Example**
```yaml
name: Deploy VelocityIQ
on:
  push:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}

  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        uses: bervProject/railway-deploy@main
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: "your-service-name"
```

---

## 🚨 **Production Checklist**

### **Security**
- [ ] Environment variables properly set
- [ ] CORS configured for production domains
- [ ] API rate limiting enabled
- [ ] Database connection pooling
- [ ] SSL/HTTPS enabled (automatic with Vercel/Railway)

### **Performance**
- [ ] Frontend build optimized
- [ ] API response caching
- [ ] Database query optimization
- [ ] CDN for static assets (automatic with Vercel)

### **Monitoring**
- [ ] Error tracking (Sentry integration)
- [ ] Performance monitoring
- [ ] Uptime monitoring
- [ ] AWS CloudWatch for SageMaker

---

## 🆘 **Troubleshooting**

### **Common Issues**

**Frontend not connecting to backend:**
```bash
# Check CORS configuration
# Verify API_URL environment variable
# Test backend endpoints directly
```

**Railway deployment fails:**
```bash
# Check Python version in runtime.txt
# Verify all dependencies in requirements.txt
# Check Railway logs: railway logs
```

**API timeouts:**
```bash
# Increase Railway service timeout
# Optimize database queries
# Add connection pooling
```

---

## 🚀 **Scaling Considerations**

### **Traffic Growth**
- **Vercel**: Automatically scales static content
- **Railway**: Upgrade to Pro for more resources
- **Database**: Supabase Pro for connection pooling
- **ML**: SageMaker auto-scaling endpoints

### **Cost Optimization**
- Use SageMaker Serverless Inference for variable ML loads
- Implement API response caching
- Optimize database queries
- Use CDN for static assets

---

**🎉 Your VelocityIQ dashboard is now production-ready on the cloud!**

Access your application:
- **Dashboard**: https://your-vercel-domain.vercel.app
- **API**: https://your-railway-app.railway.app
- **Documentation**: https://your-railway-app.railway.app/docs 