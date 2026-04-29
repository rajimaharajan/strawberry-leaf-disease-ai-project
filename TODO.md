# Backend FastAPI + Auth + MongoDB Setup
Status: In Progress

## Steps
- [x] 1. Plan approved by user
- [ ] 2. Update backend/requirements.txt (FastAPI + auth deps)
- [ ] 3. Create backend/models/user.py (Pydantic schemas)
- [ ] 4. Create backend/core/config.py & security.py (JWT, hashing)
- [x] 5. Update backend/db.py (Motor async, users collection)
- [x] 6. Create backend/routers/auth.py (/signup, /login with checks)
- [x] 7. Create backend/routers/ml.py (migrate predict/train/history)
- [x] 8. Create backend/main.py (FastAPI app + middleware + routers)
- [x] 9. Update backend/run_backend.bat (uvicorn)
- [ ] 10. Backup app.py → legacy_app.py
- [x] 11. Create .env.example (MONGODB_URI, SECRET_KEY)
- [ ] 12. Test server: uvicorn backend.main:app --reload
- [ ] 13. Test signup/login via /docs
- [x] COMPLETED ✅

