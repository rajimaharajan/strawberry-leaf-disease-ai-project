# Deployment Setup TODO

## Plan: Netlify (Frontend) + Render (Backend) + MongoDB Atlas

### Step 1: Environment-Variable-ize the Codebase
- [x] `frontend/src/api.js` — Use `REACT_APP_API_URL` env var
- [x] `backend/db.py` — Use `MONGODB_URI` env var
- [x] `backend/app.py` — Use `PORT` env var, dynamic CORS origins
- [x] `backend/requirements.txt` — Add `gunicorn`

### Step 2: Create Deployment Config Files
- [x] `frontend/.env` — Local dev API URL
- [x] `frontend/.env.production` — Production API URL template
- [x] `frontend/netlify.toml` — SPA redirect rules
- [x] `backend/Procfile` — Render start command
- [x] `backend/runtime.txt` — Ensure Python version is set
- [x] `.gitignore` — Ignore env files and large binaries

### Step 3: Create Deployment Guide
- [x] `DEPLOYMENT_GUIDE.md` — Step-by-step manual deployment instructions

### Step 4: User Action Required (Manual Deployment)
- [ ] Sign up for MongoDB Atlas → get `MONGODB_URI`
- [ ] Sign up for Render → deploy backend with env vars
- [ ] Update `frontend/.env.production` with real Render URL
- [ ] Sign up for Netlify → deploy frontend with `REACT_APP_API_URL`
- [ ] Verify frontend builds locally with `npm run build`
- [ ] Verify backend runs with `gunicorn`

