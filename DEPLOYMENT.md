# Deployment Guide

## Option 1: Railway (Recommended - Easiest)

### Backend Deployment on Railway:

1. **Create Railway Account**: Go to [railway.app](https://railway.app) and sign up with GitHub

2. **Deploy Backend**:
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login to Railway
   railway login
   
   # Initialize project
   railway init
   
   # Add environment variables
   railway variables set GROQ_API_KEY=your_groq_api_key_here
   
   # Deploy
   railway up
   ```

3. **Get Backend URL**: After deployment, Railway will provide a URL like `https://your-app.up.railway.app`

### Frontend Deployment on Vercel:

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Update Frontend API URL**:
   - Create `frontend/.env.production`:
     ```
     VITE_API_BASE_URL=https://your-railway-backend-url.up.railway.app
     ```

3. **Deploy**:
   ```bash
   cd frontend
   vercel --prod
   ```

---

## Option 2: Render + Netlify

### Backend on Render:

1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: youtube-semantic-search-backend
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     - Add `GROQ_API_KEY`
5. Add a persistent disk (optional but recommended):
   - Mount path: `/app/data`
   - Size: 10GB
6. Click "Create Web Service"

### Frontend on Netlify:

1. Go to [netlify.com](https://netlify.com) and sign up
2. Drag and drop your frontend folder OR connect GitHub
3. Build settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm install && npm run build`
   - **Publish directory**: `frontend/dist`
4. Environment variables:
   - Add `VITE_API_BASE_URL` = your Render backend URL
5. Deploy

---

## Option 3: Docker Compose (Self-hosted)

1. **Create docker-compose.yml**:
   ```yaml
   version: '3.8'
   services:
     backend:
       build:
         context: .
         dockerfile: backend/Dockerfile
       ports:
         - "8000:8000"
       environment:
         - GROQ_API_KEY=${GROQ_API_KEY}
       volumes:
         - ./data:/app/data
         - ./downloads:/app/downloads
       restart: unless-stopped
     
     frontend:
       build:
         context: ./frontend
         dockerfile: Dockerfile
       ports:
         - "80:80"
       environment:
         - VITE_API_BASE_URL=http://localhost:8000
       depends_on:
         - backend
       restart: unless-stopped
   ```

2. **Deploy**:
   ```bash
   # Create .env file with your GROQ_API_KEY
   echo "GROQ_API_KEY=your_key_here" > .env
   
   # Build and start
   docker-compose up -d
   ```

---

## Option 4: AWS (Advanced)

### Backend on AWS Elastic Beanstalk:

1. Install AWS CLI and EB CLI:
   ```bash
   pip install awsebcli
   ```

2. Initialize:
   ```bash
   eb init -p python-3.11 youtube-semantic-search
   ```

3. Create environment:
   ```bash
   eb create youtube-semantic-search-env
   ```

4. Set environment variables:
   ```bash
   eb setenv GROQ_API_KEY=your_key_here
   ```

### Frontend on AWS S3 + CloudFront:

1. Build frontend:
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. Create S3 bucket and upload:
   ```bash
   aws s3 mb s3://your-bucket-name
   aws s3 sync dist/ s3://your-bucket-name
   ```

3. Configure CloudFront distribution for the S3 bucket

---

## Environment Variables Required

### Backend:
- `GROQ_API_KEY` (required) - Your Groq API key from [console.groq.com](https://console.groq.com)
- `PORT` (optional) - Defaults to 8000

### Frontend:
- `VITE_API_BASE_URL` - Backend API URL (e.g., `https://your-backend.com`)

---

## Post-Deployment Checklist

- [ ] Backend is running and accessible
- [ ] Frontend can connect to backend API
- [ ] CORS is properly configured
- [ ] Environment variables are set
- [ ] Database persistence is working (for deployed backend)
- [ ] Test video ingestion
- [ ] Test search functionality
- [ ] Monitor logs for errors

---

## Quick Start (Railway + Vercel - 5 minutes)

**Backend:**
```bash
npm install -g @railway/cli
railway login
railway init
railway variables set GROQ_API_KEY=your_key_here
railway up
# Note the URL provided
```

**Frontend:**
```bash
cd frontend
echo "VITE_API_BASE_URL=https://your-railway-url.up.railway.app" > .env.production
npm install -g vercel
vercel --prod
```

Done! 🚀
