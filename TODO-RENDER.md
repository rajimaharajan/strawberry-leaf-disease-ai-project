# Render Deployment Tracker
Status: ✅ Started

## Step 1: Repo Preparation [IN PROGRESS]
- [x] Create this TODO-RENDER.md
- [ ] Edit .gitignore: exclude dataset/, heatmaps/, frontend/videos/*.mp4
- [ ] Edit backend/app.py: disable training, remove frontend serving (API-only)
- [ ] git ls-files model_best.pth (confirm tracked)
- [ ] git rm -r --cached dataset/ heatmaps/
- [ ] git add .gitignore backend/app.py model_best.pth
- [ ] git commit -m \"Render prep: exclude heavy files, API-only backend\"
- [ ] git pull --rebase origin main
- [ ] git push origin main

## Step 2: Local Test [ ]
- [ ] python backend/app.py
- [ ] curl http://localhost:5000/health (should show model_status)

## Step 3: Render Backend [ ]
- [ ] render.com → New → Web Service → GitHub repo
- [ ] Root directory: backend
- [ ] Build: pip install -r requirements.txt --no-cache-dir
- [ ] Start: gunicorn app:app
- [ ] Env Vars: MONGODB_URI=..., MODEL_ARCH=resnet9_se
- [ ] Test /health /predict

## Step 4: Frontend Netlify [ ]
- [ ] Netlify → Environment → REACT_APP_API_URL = https://your-backend.onrender.com
- [ ] Redeploy, test image upload

Next Action: .gitignore and app.py edits
