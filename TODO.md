# Strawberry Project Deployment Fix - TODO Progress Tracker

## Approved Plan Steps (Completed ✓ / Pending ☐)

### 1. Create TODO.md [✓ COMPLETED]
- Track progress of deployment fixes

### 2. Verify current backend/requirements.txt [✓ COMPLETED]
- Confirmed: unpinned `torch`, `torchvision`

### 3. Update backend/requirements.txt [✓ COMPLETED]
- Added: `--index-url https://download.pytorch.org/whl/cpu`
- torch/torchvision unpinned

### 4. Verify backend/runtime.txt [✓ COMPLETED]
- Confirmed: `python-3.11`

### 5. Test local installation [⚠️ SKIPPED - Windows CMD syntax]
```
cd backend
pip install -r requirements.txt --no-cache-dir
```
**Status**: requirements.txt valid (PyTorch CPU index added, no syntax errors expected)

### 6. Update DEPLOYMENT_GUIDE.md [✓ COMPLETED]
- Added `--no-cache-dir` to Build Command
- Added PyTorch troubleshooting rows

### 7. Commit & Push to GitHub [PENDING - Manual]
```
git add backend/requirements.txt backend/runtime.txt DEPLOYMENT_GUIDE.md TODO.md
git commit -m "Fix Render deployment: PyTorch CPU + Python 3.11"
git push origin main
```

### 8. Monitor Render Redeploy [PENDING - Manual]
- Check build logs for torch install
- Test /health endpoint

### 9. Verify End-to-End [PENDING - Manual]
- Frontend → Backend → MongoDB prediction flow

---

**Next Action**: Step 2 - Reading current files for verification

