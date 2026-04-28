# 🚀 Deployment Guide — Strawberry Disease Detection

## Architecture
- **Frontend**: Netlify (React SPA)
- **Backend**: Render (Flask + PyTorch)
- **Database**: MongoDB Atlas (Free Tier)

---

## Step 1: MongoDB Atlas (Database)

1. Go to [https://www.mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas) and sign up.
2. Create a **Free (M0)** cluster.
3. In **Database Access**, create a new user with password.
4. In **Network Access**, add `0.0.0.0/0` (allow from anywhere).
5. Go to **Clusters → Connect → Drivers → Python**.
6. Copy the connection string. It looks like:
   ```
   mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/strawberryDB?retryWrites=true&w=majority
   ```

---

## Step 2: Render (Backend)

1. Go to [https://render.com](https://render.com) and sign up.
2. Click **New → Web Service**.
3. Connect your **GitHub repository**.
4. Configure the service:
   - **Name**: `strawberry-backend`
   - **Environment**: `Python`
   - **Region**: Choose closest to you
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Add **Environment Variables**:
   | Key | Value |
   |-----|-------|
   | `MONGODB_URI` | Your MongoDB Atlas connection string |
   | `MODEL_ARCH` | `resnet9_se` (or `resnet18_se`) |
6. Click **Create Web Service**.
7. Wait for deployment. Once done, copy the **URL** (e.g., `https://strawberry-backend.onrender.com`).

⚠️ **Important**: The free Render tier has **cold starts** (≈30-60s). The first request after inactivity will be slow.

---

## Step 3: Netlify (Frontend)

1. Go to [https://www.netlify.com](https://www.netlify.com) and sign up.
2. Click **Add new site → Import an existing project**.
3. Connect your **GitHub repository**.
4. Configure the build:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/build`
5. Add **Environment Variable**:
   | Key | Value |
   |-----|-------|
   | `REACT_APP_API_URL` | Your Render backend URL (e.g., `https://strawberry-backend.onrender.com`) |
6. Click **Deploy**.
7. Wait for build & deploy. Netlify will give you a URL like `https://strawberry-disease.netlify.app`.

---

## Step 4: Update CORS (if needed)

If you get CORS errors after deployment:

1. In `backend/app.py`, update the CORS line:
   ```python
   from flask_cors import CORS
   # Allow specific origins
   CORS(app, origins=[
       "https://your-netlify-site.netlify.app",
       "http://localhost:3000"
   ])
   ```
2. Commit and push — Render will auto-redeploy.

---

## Step 5: Upload Model File

Ensure `model_best.pth` is in your Git repo at the **project root** (same level as `backend/` and `frontend/`). If it's too large for Git:

1. Upload it to **Google Drive / Dropbox**.
2. Add a download step in Render's build command:
   ```bash
   pip install -r requirements.txt && curl -L "YOUR_DOWNLOAD_LINK" -o model_best.pth
   ```

Or use **Git LFS** for large files.

---

## Local Development (After These Changes)

```bash
# Terminal 1 — Backend
cd backend
pip install -r requirements.txt
python app.py

# Terminal 2 — Frontend
cd frontend
npm install
npm start
```

The frontend will use `http://localhost:5000` (from `.env`) automatically.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Model not loaded` on Render | Ensure `model_best.pth` is in repo or downloaded during build |
| CORS errors | Add your Netlify URL to `CORS(app, origins=[...])` |
| MongoDB timeout | Check `MONGODB_URI` has correct password and IP whitelist `0.0.0.0/0` |
| Frontend shows blank page | Check browser console for API errors; verify `REACT_APP_API_URL` |
| Render cold start | Free tier sleeps after 15 min; first request wakes it up (~30-60s) |

---

## Useful Links

- **Render Dashboard**: https://dashboard.render.com
- **Netlify Dashboard**: https://app.netlify.com
- **MongoDB Atlas**: https://cloud.mongodb.com

