# 🚀 Quick Deployment Checklist

## ✅ Pre-Deployment Tasks

### 1. Update Frontend to Use Environment Variables
- [ ] Import API config in all files that make API calls
- [ ] Replace hardcoded URLs with config endpoints
- [ ] Test locally to ensure everything still works

### 2. Prepare Backend
- [ ] Ensure all dependencies are in `requirements.txt`
- [ ] Update CORS settings to allow your frontend domain
- [ ] Test backend locally

### 3. Git Repository
- [ ] Commit all changes
- [ ] Push to GitHub

## 🎯 Recommended Deployment Path

### Option A: Render (Full-Stack)
**Best for**: Deploying everything in one place

1. [ ] Sign up at [render.com](https://render.com)
2. [ ] Click "New +" → "Blueprint"
3. [ ] Connect your GitHub repository
4. [ ] Render will detect `render.yaml`
5. [ ] Add environment variables:
   - Backend: `GOOGLE_API_KEY`
   - Frontend: `NEXT_PUBLIC_API_URL` (will be your backend URL)
6. [ ] Click "Apply" and wait for deployment
7. [ ] Update frontend `NEXT_PUBLIC_API_URL` with deployed backend URL
8. [ ] Redeploy frontend

**Estimated time**: 15-20 minutes

---

### Option B: Vercel (Frontend) + Render (Backend)
**Best for**: Maximum Next.js performance

#### Step 1: Deploy Backend to Render
1. [ ] Go to [render.com](https://render.com)
2. [ ] New Web Service → Connect GitHub
3. [ ] Select repository, choose `career-backend` folder
4. [ ] Build Command: `pip install -r requirements.txt`
5. [ ] Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. [ ] Add environment variable: `GOOGLE_API_KEY`
7. [ ] Deploy and note the URL (e.g., `https://skillfit-backend.onrender.com`)

#### Step 2: Deploy Frontend to Vercel
1. [ ] Go to [vercel.com](https://vercel.com)
2. [ ] Import your GitHub repository
3. [ ] Set Root Directory: `new-career-frontend`
4. [ ] Add environment variable: `NEXT_PUBLIC_API_URL` = your backend URL from Step 1
5. [ ] Deploy

**Estimated time**: 20-25 minutes

---

### Option C: Netlify (Frontend) + Render (Backend)
**Best for**: Alternative to Vercel

#### Step 1: Deploy Backend to Render
Same as Option B, Step 1

#### Step 2: Deploy Frontend to Netlify
1. [ ] Go to [netlify.com](https://netlify.com)
2. [ ] Add new site → Import from Git
3. [ ] Connect GitHub repository
4. [ ] Base directory: `new-career-frontend`
5. [ ] Build command: `npm run build`
6. [ ] Publish directory: `.next`
7. [ ] Add environment variable: `NEXT_PUBLIC_API_URL` = your backend URL
8. [ ] Deploy

**Estimated time**: 20-25 minutes

---

## 🔑 Environment Variables Reference

### Backend (Render)
```
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

### Frontend (Vercel/Netlify/Render)
```
NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
```

---

## 🧪 Post-Deployment Testing

1. [ ] Visit your deployed frontend URL
2. [ ] Test sign up functionality
3. [ ] Test sign in functionality
4. [ ] Upload a resume and job description
5. [ ] Verify analysis results display correctly
6. [ ] Test the AI chat feature
7. [ ] Check browser console for any errors

---

## 🐛 Common Issues & Solutions

### Issue: Frontend can't connect to backend
**Solution**: 
- Check `NEXT_PUBLIC_API_URL` is set correctly
- Verify backend is running (check Render logs)
- Update CORS settings in backend

### Issue: Build fails on Render
**Solution**:
- Check Python version (should be 3.10+)
- Verify all dependencies in `requirements.txt`
- Check build logs for specific errors

### Issue: Environment variables not working
**Solution**:
- Vercel/Netlify: Must start with `NEXT_PUBLIC_`
- Rebuild after adding new variables
- Clear cache and redeploy

### Issue: Database resets on Render
**Solution**:
- Render free tier has ephemeral storage
- Consider upgrading or using external database
- For demo purposes, this is acceptable

---

## 📱 Your Deployed URLs

After deployment, fill in your URLs here:

- **Frontend**: ___________________________________
- **Backend**: ___________________________________
- **Admin Panel**: ___________________________________

---

## 🎉 Next Steps After Deployment

1. [ ] Update README.md with live demo link
2. [ ] Share your project on LinkedIn/Twitter
3. [ ] Add custom domain (optional)
4. [ ] Set up monitoring/analytics
5. [ ] Consider upgrading to paid tier for better performance

---

**Need Help?** Refer to the full `DEPLOYMENT_GUIDE.md` for detailed instructions!
