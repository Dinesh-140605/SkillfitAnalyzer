# SkillFit Analyzer - Deployment Guide

This guide covers deploying your full-stack application to **Render**, **Vercel**, and **Netlify**.

---

## 🏗️ Project Architecture

- **Frontend**: Next.js 14 (TypeScript + Tailwind CSS)
- **Backend**: FastAPI (Python)
- **Database**: SQLite (career_compass.db)

---

## 📋 Pre-Deployment Checklist

### 1. Environment Variables
Your backend needs the following environment variable:
- `GOOGLE_API_KEY` - Your Google Gemini API key

### 2. Update API URLs
Before deploying, you'll need to update the frontend to use your deployed backend URL instead of `http://127.0.0.1:8000`.

---

## 🚀 Option 1: Deploy to Render (Recommended for Full-Stack)

**Why Render?** Render supports both frontend and backend on the same platform with a free tier.

### Step 1: Prepare Backend for Render

1. **Create `render.yaml`** in your project root:

```yaml
services:
  # Backend Service
  - type: web
    name: skillfit-backend
    env: python
    buildCommand: "pip install -r career-backend/requirements.txt"
    startCommand: "cd career-backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: GOOGLE_API_KEY
        sync: false
      - key: PYTHON_VERSION
        value: 3.11.0

  # Frontend Service
  - type: web
    name: skillfit-frontend
    env: node
    buildCommand: "cd new-career-frontend && npm install && npm run build"
    startCommand: "cd new-career-frontend && npm start"
    envVars:
      - key: NODE_VERSION
        value: 18.17.0
      - key: NEXT_PUBLIC_API_URL
        sync: false
```

2. **Update Backend CORS** - Edit `career-backend/app/main.py` to allow your frontend domain:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your frontend URL after deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 2: Deploy to Render

1. **Push to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Create Render Account**: Go to [render.com](https://render.com) and sign up

3. **Create New Web Service**:
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will detect `render.yaml` and create both services

4. **Set Environment Variables**:
   - For backend: Add `GOOGLE_API_KEY`
   - For frontend: Add `NEXT_PUBLIC_API_URL` (your backend URL)

5. **Deploy**: Click "Apply" and wait for deployment

**Your URLs will be**:
- Backend: `https://skillfit-backend.onrender.com`
- Frontend: `https://skillfit-frontend.onrender.com`

---

## 🔷 Option 2: Deploy to Vercel (Frontend) + Render (Backend)

**Why this combo?** Vercel is optimized for Next.js, and Render handles the Python backend.

### Step 1: Deploy Backend to Render

1. **Create `career-backend/render.yaml`**:

```yaml
services:
  - type: web
    name: skillfit-backend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: GOOGLE_API_KEY
        sync: false
```

2. Go to [render.com](https://render.com) → New Web Service
3. Connect repository and select `career-backend` folder
4. Add `GOOGLE_API_KEY` environment variable
5. Deploy and note your backend URL

### Step 2: Deploy Frontend to Vercel

1. **Install Vercel CLI** (optional):
   ```bash
   npm i -g vercel
   ```

2. **Update API URL** - Create `new-career-frontend/.env.production`:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
   ```

3. **Deploy via Vercel Dashboard**:
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New" → "Project"
   - Import your GitHub repository
   - Set **Root Directory** to `new-career-frontend`
   - Add environment variable: `NEXT_PUBLIC_API_URL`
   - Click "Deploy"

4. **Or Deploy via CLI**:
   ```bash
   cd new-career-frontend
   vercel --prod
   ```

**Your URLs**:
- Backend: `https://skillfit-backend.onrender.com`
- Frontend: `https://skillfit-analyzer.vercel.app`

---

## 🟢 Option 3: Deploy to Netlify (Frontend) + Render (Backend)

### Step 1: Deploy Backend to Render
Follow the same steps as Option 2, Step 1.

### Step 2: Deploy Frontend to Netlify

1. **Create `new-career-frontend/netlify.toml`**:

```toml
[build]
  command = "npm run build"
  publish = ".next"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

2. **Update API URL** - Create `new-career-frontend/.env.production`:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
   ```

3. **Deploy via Netlify Dashboard**:
   - Go to [netlify.com](https://netlify.com)
   - Click "Add new site" → "Import an existing project"
   - Connect GitHub repository
   - Set **Base directory** to `new-career-frontend`
   - Set **Build command** to `npm run build`
   - Set **Publish directory** to `.next`
   - Add environment variable: `NEXT_PUBLIC_API_URL`
   - Click "Deploy"

4. **Or Deploy via Netlify CLI**:
   ```bash
   npm install -g netlify-cli
   cd new-career-frontend
   netlify deploy --prod
   ```

**Your URLs**:
- Backend: `https://skillfit-backend.onrender.com`
- Frontend: `https://skillfit-analyzer.netlify.app`

---

## 🔧 Important Post-Deployment Steps

### 1. Update Frontend API Calls

Find all instances of `http://127.0.0.1:8000` in your frontend and replace with environment variable:

```typescript
// Instead of:
const API_URL = "http://127.0.0.1:8000";

// Use:
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
```

### 2. Update Backend CORS

In `career-backend/app/main.py`, update allowed origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.vercel.app",
        "https://your-frontend.netlify.app",
        "http://localhost:3005"  # Keep for local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Database Considerations

⚠️ **Important**: SQLite (`career_compass.db`) won't persist on Render's free tier (ephemeral filesystem).

**Solutions**:
- **Option A**: Use Render's PostgreSQL (free tier available)
- **Option B**: Use a managed database (Supabase, PlanetScale)
- **Option C**: Accept that data resets on each deployment (for demo purposes)

---

## 📊 Comparison Table

| Platform | Frontend | Backend | Free Tier | Best For |
|----------|----------|---------|-----------|----------|
| **Render** | ✅ | ✅ | 750 hrs/month | Full-stack in one place |
| **Vercel** | ✅ | ❌ | Unlimited | Next.js apps |
| **Netlify** | ✅ | ❌ | 300 build mins | Static sites |

---

## 🎯 My Recommendation

**For your project, I recommend**:

1. **Backend**: Deploy to **Render** (free Python hosting)
2. **Frontend**: Deploy to **Vercel** (best Next.js performance)

This gives you:
- ✅ Best performance for Next.js
- ✅ Free hosting for both services
- ✅ Easy environment variable management
- ✅ Automatic deployments from GitHub

---

## 🆘 Troubleshooting

### Build Fails on Render
- Check Python version matches your local (3.10+)
- Ensure all dependencies are in `requirements.txt`

### Frontend Can't Connect to Backend
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS settings in backend
- Ensure backend is running (check Render logs)

### Environment Variables Not Working
- Vercel/Netlify: Must start with `NEXT_PUBLIC_`
- Render: Don't need prefix
- Rebuild after adding new variables

---

## 📝 Quick Commands Reference

```bash
# Check if git is initialized
git status

# Add all files
git add .

# Commit changes
git commit -m "Prepare for deployment"

# Push to GitHub
git push origin main

# Install Vercel CLI
npm i -g vercel

# Deploy to Vercel
cd new-career-frontend && vercel --prod

# Install Netlify CLI
npm i -g netlify-cli

# Deploy to Netlify
cd new-career-frontend && netlify deploy --prod
```

---

**Need help?** Let me know which platform you'd like to deploy to, and I can help you with the specific steps!
