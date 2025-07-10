# 🐳 VelocityIQ Deployment Guide: Docker

## **Option 3: Docker Deployment (Quick & Simple)**

### **Architecture Overview**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │    │   Docker        │    │   Supabase      │
│   (Frontend)    │───▶│   Backend       │───▶│   (Database)    │
│   React Build   │    │   FastAPI       │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  AWS SageMaker  │
                       │  (Chronos ML)   │
                       └─────────────────┘
```

---

## 🚀 **Step 1: Create Docker Configuration**

### **1.1 Backend Dockerfile**
Create `Dockerfile.backend`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements_dashboard.txt .
RUN pip install --no-cache-dir -r requirements_dashboard.txt

# Copy application code
COPY dashboard_api_fixed.py .
COPY supabase_forecasting_integration.py .
COPY *.py .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "dashboard_api_fixed:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **1.2 Frontend Dockerfile**
Create `Dockerfile.frontend`:
```dockerfile
# Build stage
FROM node:16-alpine as build

WORKDIR /app

# Copy package files
COPY dashboard/package*.json ./
RUN npm install

# Copy source code and build
COPY dashboard/ ./
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built React app
COPY --from=build /app/build /usr/share/nginx/html

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

### **1.3 Nginx Configuration**
Create `nginx.conf`:
```nginx
server {
    listen 80;
    server_name localhost;

    # Serve React app
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to backend
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}
```

---

## 🐳 **Step 2: Docker Compose Setup**

### **2.1 Create docker-compose.yml**
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: velocityiq-backend
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - velocityiq-network

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: velocityiq-frontend
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    ports:
      - "80:80"
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - velocityiq-network

  # Optional: Redis for caching
  redis:
    image: redis:7-alpine
    container_name: velocityiq-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes
    networks:
      - velocityiq-network

volumes:
  redis_data:

networks:
  velocityiq-network:
    driver: bridge
```

### **2.2 Create Production docker-compose.prod.yml**
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: velocityiq-backend-prod
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}
      - ENVIRONMENT=production
    expose:
      - "8000"
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    networks:
      - velocityiq-network

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
      args:
        - REACT_APP_API_URL=https://your-domain.com
    container_name: velocityiq-frontend-prod
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    networks:
      - velocityiq-network

  # Nginx Load Balancer
  nginx:
    image: nginx:alpine
    container_name: velocityiq-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx-prod.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
    networks:
      - velocityiq-network

networks:
  velocityiq-network:
    driver: bridge
```

---

## 🔧 **Step 3: Environment Setup**

### **3.1 Create .env File**
```bash
# Create .env file
cat > .env << 'EOF'
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO

# Optional: Redis Configuration
REDIS_URL=redis://redis:6379

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
EOF
```

### **3.2 Create Production nginx-prod.conf**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    server {
        listen 80;
        server_name your-domain.com;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;

        # Security Headers
        add_header Strict-Transport-Security "max-age=63072000" always;
        add_header X-Frame-Options DENY always;
        add_header X-Content-Type-Options nosniff always;
        add_header Referrer-Policy no-referrer-when-downgrade always;

        # API requests
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

---

## 🚀 **Step 4: Deployment Commands**

### **4.1 Development Deployment**
```bash
# Build and start services
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Clean up (remove volumes)
docker-compose down -v
```

### **4.2 Production Deployment**
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Scale backend for high availability
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Update single service
docker-compose -f docker-compose.prod.yml up -d --no-deps backend

# View production logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

### **4.3 Maintenance Commands**
```bash
# View running containers
docker ps

# Check container health
docker-compose ps

# Execute commands in running container
docker exec -it velocityiq-backend bash

# View container logs
docker logs velocityiq-backend

# Restart specific service
docker-compose restart backend

# Update and restart services
docker-compose pull && docker-compose up -d

# Clean up unused images
docker image prune -f

# Backup volumes
docker run --rm -v velocityiq_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup.tar.gz -C /data .
```

---

## 📊 **Step 5: Monitoring & Health Checks**

### **5.1 Create Health Check Script**
Create `scripts/health-check.sh`:
```bash
#!/bin/bash

# Health check script for VelocityIQ services

echo "🔍 Checking VelocityIQ services..."

# Check backend health
echo "Backend health:"
curl -f http://localhost:8000/health || echo "❌ Backend unhealthy"

# Check frontend health
echo "Frontend health:"
curl -f http://localhost/health || echo "❌ Frontend unhealthy"

# Check database connectivity
echo "Database connectivity:"
docker exec velocityiq-backend python -c "
import os
from supabase import create_client, Client
try:
    supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
    result = supabase.table('products').select('*').limit(1).execute()
    print('✅ Database connected')
except Exception as e:
    print(f'❌ Database error: {e}')
"

# Check Redis (if enabled)
if docker ps --filter "name=velocityiq-redis" --format "table {{.Names}}" | grep -q redis; then
    echo "Redis status:"
    docker exec velocityiq-redis redis-cli ping || echo "❌ Redis unhealthy"
fi

# Check container resources
echo "Container resource usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo "🎉 Health check complete!"
```

Make it executable:
```bash
chmod +x scripts/health-check.sh
```

### **5.2 Create Monitoring docker-compose.monitoring.yml**
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: velocityiq-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    networks:
      - velocityiq-network

  grafana:
    image: grafana/grafana:latest
    container_name: velocityiq-grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - velocityiq-network

volumes:
  prometheus_data:
  grafana_data:

networks:
  velocityiq-network:
    external: true
```

---

## 🔄 **Step 6: Backup & Recovery**

### **6.1 Create Backup Script**
Create `scripts/backup.sh`:
```bash
#!/bin/bash

BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "🔄 Creating backup in $BACKUP_DIR..."

# Backup application data
echo "Backing up logs..."
docker cp velocityiq-backend:/app/logs $BACKUP_DIR/logs

# Backup Redis data (if available)
if docker ps --filter "name=velocityiq-redis" --format "table {{.Names}}" | grep -q redis; then
    echo "Backing up Redis data..."
    docker exec velocityiq-redis redis-cli BGSAVE
    docker cp velocityiq-redis:/data $BACKUP_DIR/redis
fi

# Backup environment configuration
echo "Backing up configuration..."
cp .env $BACKUP_DIR/
cp docker-compose*.yml $BACKUP_DIR/

# Create archive
echo "Creating archive..."
tar -czf $BACKUP_DIR.tar.gz -C $BACKUP_DIR .
rm -rf $BACKUP_DIR

echo "✅ Backup completed: $BACKUP_DIR.tar.gz"
```

### **6.2 Create Restore Script**
Create `scripts/restore.sh`:
```bash
#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

BACKUP_FILE=$1
RESTORE_DIR="./restore_$(date +%Y%m%d_%H%M%S)"

echo "🔄 Restoring from $BACKUP_FILE..."

# Extract backup
mkdir -p $RESTORE_DIR
tar -xzf $BACKUP_FILE -C $RESTORE_DIR

# Stop services
docker-compose down

# Restore configuration
cp $RESTORE_DIR/.env ./
cp $RESTORE_DIR/docker-compose*.yml ./

# Restore Redis data
if [ -d "$RESTORE_DIR/redis" ]; then
    docker volume create velocityiq_redis_data
    docker run --rm -v velocityiq_redis_data:/data -v $RESTORE_DIR/redis:/backup alpine cp -r /backup/* /data/
fi

# Start services
docker-compose up -d

# Clean up
rm -rf $RESTORE_DIR

echo "✅ Restore completed!"
```

---

## 💰 **Cost Estimation (Docker Deployment)**

### **Infrastructure Costs**
- **VPS/Cloud Instance**: ~$10-50/month (2-4GB RAM)
- **Domain & SSL**: ~$10-20/year
- **Backup Storage**: ~$5-10/month
- **Monitoring (optional)**: ~$0-20/month

**Total: ~$15-80/month**

### **Recommended VPS Specs**
- **CPU**: 2+ cores
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 50GB SSD minimum
- **Bandwidth**: 1TB/month

---

## 🔧 **Quick Start Commands**

### **Complete Setup (One-Click)**
```bash
# Clone and setup
git clone <your-repo>
cd VelocityIQ

# Copy environment template
cp .env.example .env
# Edit .env with your credentials

# Make scripts executable
chmod +x scripts/*.sh

# Build and start
docker-compose up -d --build

# Check health
./scripts/health-check.sh

# View dashboard
open http://localhost
```

### **Daily Operations**
```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f backend

# Update application
git pull
docker-compose up -d --build

# Backup data
./scripts/backup.sh

# Monitor resources
docker stats
```

---

**🎉 Your VelocityIQ dashboard is now running in Docker!**

Access your application at:
- **Dashboard**: http://localhost
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Monitoring**: http://localhost:3001 (if enabled)

This Docker setup provides:
- ✅ **Containerized Deployment**: Easy scaling and management
- ✅ **Health Monitoring**: Built-in health checks
- ✅ **Load Balancing**: Nginx proxy for production
- ✅ **Backup/Restore**: Automated data protection
- ✅ **Cost Effective**: Single server deployment 