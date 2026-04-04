# Deployment Guide
## Sidekick Medical Assistant Backend

**Version:** 1.0.0  
**Last Updated:** March 9, 2026

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Staging Deployment](#staging-deployment)
4. [Production Deployment](#production-deployment)
5. [Database Setup](#database-setup)
6. [Environment Configuration](#environment-configuration)
7. [Monitoring Setup](#monitoring-setup)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- Python 3.13 or higher
- pip (Python package manager)
- Git
- PostgreSQL 14+ (for production) OR SQLite (for development)

### Required Accounts

- Google Cloud (for Gemini API)
- Supabase (for PostgreSQL database)
- Deployment platform (Render, Railway, or AWS)

---

## Local Development

### 1. Clone Repository

```bash
git clone <repository-url>
cd sidekick-medical-assistant
```

### 2. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Configure Environment

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Database (SQLite for development)
DATABASE_URL=sqlite+aiosqlite:///./sidekick.db

# Server
HOST=127.0.0.1
PORT=8000
```

### 4. Initialize Database

```bash
python test_database_sqlite.py
```

### 5. Start Server

```bash
python start_server.py
```

Server will be available at: `http://127.0.0.1:8000`

### 6. Verify Installation

```bash
# Health check
curl http://127.0.0.1:8000/health

# Run tests
python run_complete_test_suite.py

# Run E2E test
python test_e2e_integration.py
```

---

## Staging Deployment

### Option 1: Render.com

#### 1. Create New Web Service

- Go to [Render Dashboard](https://dashboard.render.com/)
- Click "New +" → "Web Service"
- Connect your Git repository

#### 2. Configure Service

```yaml
Name: sidekick-backend-staging
Environment: Python 3
Build Command: pip install -r backend/requirements.txt
Start Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

#### 3. Set Environment Variables

```env
GEMINI_API_KEY=<your-key>
DATABASE_URL=<supabase-url>
PYTHON_VERSION=3.13.0
```

#### 4. Deploy

- Click "Create Web Service"
- Wait for deployment to complete
- Note the URL: `https://sidekick-backend-staging.onrender.com`

### Option 2: Railway.app

#### 1. Create New Project

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init
```

#### 2. Configure Project

```bash
# Set environment variables
railway variables set GEMINI_API_KEY=<your-key>
railway variables set DATABASE_URL=<supabase-url>

# Deploy
railway up
```

#### 3. Get URL

```bash
railway domain
```

### Option 3: AWS EC2

#### 1. Launch EC2 Instance

- AMI: Ubuntu 22.04 LTS
- Instance Type: t3.small (minimum)
- Security Group: Allow ports 22, 80, 443

#### 2. Connect and Setup

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@<instance-ip>

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.13
sudo apt install python3.13 python3.13-venv python3-pip -y

# Clone repository
git clone <repository-url>
cd sidekick-medical-assistant

# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

#### 3. Configure Environment

```bash
# Create .env file
nano .env

# Add environment variables
GEMINI_API_KEY=<your-key>
DATABASE_URL=<supabase-url>
HOST=0.0.0.0
PORT=8000
```

#### 4. Set Up Systemd Service

```bash
sudo nano /etc/systemd/system/sidekick.service
```

```ini
[Unit]
Description=Sidekick Medical Assistant Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/sidekick-medical-assistant
Environment="PATH=/home/ubuntu/sidekick-medical-assistant/venv/bin"
ExecStart=/home/ubuntu/sidekick-medical-assistant/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable sidekick
sudo systemctl start sidekick
sudo systemctl status sidekick
```

#### 5. Set Up Nginx Reverse Proxy

```bash
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/sidekick
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/sidekick /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 6. Set Up SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Code review complete
- [ ] Security audit complete
- [ ] Load testing complete
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] Rollback plan documented
- [ ] Team notified

### Deployment Steps

1. **Deploy to Production Environment**
   - Follow staging deployment steps
   - Use production environment variables
   - Use production database

2. **Verify Deployment**
   ```bash
   # Health check
   curl https://api.your-domain.com/health
   
   # Run smoke tests
   python test_e2e_integration.py --url https://api.your-domain.com
   ```

3. **Monitor for Issues**
   - Check logs for errors
   - Monitor response times
   - Watch error rates
   - Verify database connections

4. **Enable Traffic**
   - Update DNS if needed
   - Enable load balancer
   - Monitor traffic

---

## Database Setup

### Supabase PostgreSQL

#### 1. Create Project

- Go to [Supabase Dashboard](https://app.supabase.com/)
- Click "New Project"
- Choose region closest to your users
- Set strong database password

#### 2. Get Connection String

- Go to Project Settings → Database
- Copy "Connection string" under "Connection pooling"
- Format: `postgresql://postgres:[password]@[host]:6543/postgres`

#### 3. Initialize Database

The database will auto-initialize on first server startup. Tables will be created automatically.

#### 4. Verify Connection

```bash
python test_database.py
```

### SQLite (Development Only)

SQLite is automatically configured for local development. No setup required.

---

## Environment Configuration

### Required Variables

```env
# API Keys
GEMINI_API_KEY=<your-gemini-api-key>

# Database
DATABASE_URL=<postgresql-or-sqlite-url>

# Server (optional)
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Security (production)
ALLOWED_ORIGINS=https://your-frontend-domain.com
```

### Optional Variables

```env
# Performance
MAX_CONNECTIONS=20
QUERY_TIMEOUT=30

# Monitoring
SENTRY_DSN=<your-sentry-dsn>
LOG_LEVEL=DEBUG
```

---

## Monitoring Setup

### Health Checks

Set up automated health checks:

```bash
# Uptime monitoring
curl https://api.your-domain.com/health

# Expected response
{"status":"healthy","service":"Sidekick Medical Assistant","version":"1.0.0"}
```

### Logging

Logs are written to stdout. Configure log aggregation:

- **Render/Railway:** Built-in log viewer
- **AWS:** CloudWatch Logs
- **Self-hosted:** ELK Stack or Grafana Loki

### Metrics

Monitor these metrics:

- Response times (p50, p95, p99)
- Error rates
- Database connection pool usage
- Memory usage
- CPU usage

### Alerts

Set up alerts for:

- Health check failures
- Error rate > 1%
- Response time > 2s
- Database connection failures
- Memory usage > 80%

---

## Troubleshooting

### Server Won't Start

**Problem:** Server fails to start

**Solutions:**
1. Check environment variables are set
2. Verify database connection
3. Check port is not in use
4. Review logs for errors

```bash
# Check logs
tail -f /var/log/sidekick/error.log

# Test database connection
python test_database.py

# Check port
lsof -i :8000
```

### Database Connection Errors

**Problem:** Can't connect to database

**Solutions:**
1. Verify DATABASE_URL is correct
2. Check network connectivity
3. Verify database credentials
4. Check firewall rules

```bash
# Test connection
psql $DATABASE_URL

# Check DNS
nslookup your-database-host.com
```

### High Response Times

**Problem:** API is slow

**Solutions:**
1. Check database query performance
2. Review performance logs
3. Check AI service response times
4. Verify network latency

```bash
# Check performance logs
grep "Performance:" /var/log/sidekick/app.log

# Monitor database
psql $DATABASE_URL -c "SELECT * FROM pg_stat_activity;"
```

### WebSocket Connection Failures

**Problem:** WebSocket won't connect

**Solutions:**
1. Verify WSS is enabled (production)
2. Check CORS configuration
3. Verify proxy configuration
4. Check firewall rules

```bash
# Test WebSocket
wscat -c wss://api.your-domain.com/ws/session
```

### Memory Leaks

**Problem:** Memory usage increasing

**Solutions:**
1. Check for unclosed database connections
2. Review WebSocket connection cleanup
3. Monitor connection pool
4. Restart service if needed

```bash
# Check memory
free -h

# Restart service
sudo systemctl restart sidekick
```

---

## Rollback Procedure

If deployment fails:

1. **Immediate Rollback**
   ```bash
   # Render/Railway
   railway rollback
   
   # AWS
   git checkout previous-version
   sudo systemctl restart sidekick
   ```

2. **Verify Rollback**
   ```bash
   curl https://api.your-domain.com/health
   ```

3. **Investigate Issue**
   - Review deployment logs
   - Check error logs
   - Identify root cause

4. **Fix and Redeploy**
   - Fix issue in code
   - Test locally
   - Deploy again

---

## Backup and Recovery

### Automated Backups

Configure daily backups:

```bash
# Supabase: Automatic backups enabled
# Self-hosted PostgreSQL:
pg_dump $DATABASE_URL > backup-$(date +%Y%m%d).sql
```

### Manual Backup

```bash
# Create backup
pg_dump $DATABASE_URL > manual-backup.sql

# Restore backup
psql $DATABASE_URL < manual-backup.sql
```

### Disaster Recovery

1. Restore from latest backup
2. Verify data integrity
3. Restart services
4. Run smoke tests
5. Monitor for issues

---

## Security Checklist

### Pre-Production

- [ ] HTTPS enabled
- [ ] WSS enabled for WebSocket
- [ ] Environment variables secured
- [ ] Database credentials rotated
- [ ] API keys secured
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] Authentication implemented
- [ ] Input validation active
- [ ] Log sanitization enabled

### Post-Production

- [ ] Monitor for security issues
- [ ] Regular security audits
- [ ] Keep dependencies updated
- [ ] Review access logs
- [ ] Rotate credentials regularly

---

## Support

### Documentation

- [README.md](README.md) - Project overview
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing instructions
- [QUICK_START.md](QUICK_START.md) - Quick start guide
- [API Documentation](http://127.0.0.1:8000/docs) - Swagger UI

### Contact

- **Backend Team:** backend@your-company.com
- **DevOps Team:** devops@your-company.com
- **On-Call:** oncall@your-company.com

---

**Last Updated:** March 9, 2026  
**Version:** 1.0.0  
**Status:** Production Ready
