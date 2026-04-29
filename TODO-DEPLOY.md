# Backend Deployment Tracker — Render + MongoDB Atlas

Repo: https://github.com/rajimaharajan/strawberry-leaf-disease-ai-project

## Steps [Pending ☐ / Complete ✓]

### 1. Fix .gitignore for model_best.pth [PENDING]
```
edit_file .gitignore "*.pth" "# *.pth"
git add model_best.pth .gitignore
git commit -m \"Add model_best.pth for deployment\"
git push
```

### 2. Deploy Backend to Render [PENDING]
```
1. render.com → New → Web Service → Connect GitHub repo
2. Root Directory: backend
3. Build: pip install -r requirements.txt --no-cache-dir
4. Start: gunicorn app:app
5. Env Vars:
   MONGODB_URI=your_atlas_uri
   MODEL_ARCH=resnet9_se
```
Expected URL: https://your-app.onrender.com

### 3. MongoDB Atlas Setup [PENDING]
```
1. cloud.mongodb.com → New Cluster (M0 Free)
2. Database User: strawberry / [password]
3. Network: 0.0.0.0/0
4. Get URI: mongodb+srv://strawberry:[pwd]@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

### 4. Update Frontend Netlify [PENDING]
```
Netlify → Site Settings → Environment → REACT_APP_API_URL = https://your-render.onrender.com
→ Redeploy
```

### 5. Test End-to-End [PENDING]
```
curl [render-url]/health
Netlify → Upload image → Analyze → Check MongoDB Atlas collection
```

### 6. CORS Update (if needed) [PENDING]
```
CORS(app, origins=[\"https://your-netlify.netlify.app\"])
git push → Render redeploys
```

**Next: Step 1 → User provides Netlify URL + Atlas URI → Deploy!**

