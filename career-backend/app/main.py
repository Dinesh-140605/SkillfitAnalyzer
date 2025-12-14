# main.py
from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Any
import io
import hashlib
import os

# Try to import pdfplumber for PDF parsing (optional)
try:
    import pdfplumber
except Exception:
    pdfplumber = None

# Import local modules - adjust if your layout differs
from .analyzer import Analyzer
from .database import (
    register_user,
    login_user,
    save_analysis,
    get_user_history,
    delete_history_entry,
    get_all_users,
    get_all_history,
    get_user_details,
)

app = FastAPI(title="Career Compass Backend", version="1.0")

# CORS - allow your frontend origin(s) or use ["*"] in dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Admin credentials (hardcoded)
# -------------------------
ADMIN_EMAIL = "dds14061995@gmail.com"
# NOTE: store only a hash here (we compare a hash)
ADMIN_PASSWORD_HASH = hashlib.sha256("Dinesh@14".encode()).hexdigest()

# -------------------------
# Instantiate Analyzer on startup
# -------------------------
analyzer: Optional[Analyzer] = None


@app.on_event("startup")
def startup_event():
    global analyzer
    analyzer = Analyzer()


# -------------------------
# Pydantic models
# -------------------------
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class SaveAnalysisRequest(BaseModel):
    user_id: int
    jd_text: str
    resume_text: str
    analysis_result: dict


# -------------------------
# Utility helpers
# -------------------------
def verify_admin(admin_email: str, admin_password: str) -> bool:
    if admin_email != ADMIN_EMAIL:
        return False
    return hashlib.sha256(admin_password.encode()).hexdigest() == ADMIN_PASSWORD_HASH


# -------------------------
# Routers (modular)
# -------------------------
auth_router = APIRouter(prefix="/auth", tags=["auth"])
analysis_router = APIRouter(prefix="/analysis", tags=["analysis"])
history_router = APIRouter(prefix="/history", tags=["history"])
admin_router = APIRouter(prefix="/admin", tags=["admin"])


# -------------------------
# Auth endpoints
# -------------------------
@auth_router.post("/register")
async def api_register(req: RegisterRequest):
    """Register a new user"""
    res = register_user(req.name, req.email, req.password)
    # Ensure consistent response format
    if isinstance(res, dict) and res.get("success") is not None:
        return res
    return {"success": True, "message": "Registered", "data": res}


@auth_router.post("/login")
async def api_login(req: LoginRequest):
    """Login user"""
    res = login_user(req.email, req.password)
    if isinstance(res, dict) and res.get("success") is not None:
        return res
    return {"success": True, "message": "Logged in", "data": res}


# -------------------------
# Analysis endpoints
# -------------------------
@analysis_router.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    """Return extracted text from resume pdf/txt"""
    content = await file.read()
    if pdfplumber and file.filename.lower().endswith(".pdf"):
        try:
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception:
            text = content.decode(errors="ignore")
    else:
        text = content.decode(errors="ignore")
    return {"text": text}


@analysis_router.post("/full-analyze")
async def full_analyze(jd_text: str = Form(...), resume_text: str = Form(...)):
    """Run Analyzer and return structured result"""
    global analyzer
    if analyzer is None:
        analyzer = Analyzer()
    try:
        result = analyzer.analyze(resume_text, jd_text)
        # ensure types friendly to JSON
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


class ChatRequest(BaseModel):
    message: str
    context: dict

@analysis_router.post("/chat")
async def chat_endpoint(req: ChatRequest):
    """Chat with AI Coach using context"""
    global analyzer
    if analyzer is None:
        analyzer = Analyzer()
    
    try:
        response_text = analyzer.chat_coach(req.message, req.context)
        return {"response": response_text}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}


# -------------------------
# History endpoints (user-specific)
# -------------------------
@history_router.post("/save")
async def api_save_analysis(req: SaveAnalysisRequest):
    """Save analysis into user's history"""
    try:
        res = save_analysis(req.user_id, req.jd_text, req.resume_text, req.analysis_result)
        return {"success": True, "message": "Saved", "data": res}
    except Exception as e:
        return {"success": False, "message": f"Save failed: {e}"}


@history_router.get("/{user_id}")
async def api_get_history(user_id: int, limit: int = 50):
    """Get history for a user"""
    try:
        res = get_user_history(user_id, limit)
        return {"success": True, "history": res.get("history", res) if isinstance(res, dict) else res}
    except Exception as e:
        return {"success": False, "message": f"Failed to fetch history: {e}"}


@history_router.delete("/{history_id}")
async def api_delete_history(history_id: int, user_id: int):
    """Delete a specific history entry for user"""
    try:
        res = delete_history_entry(history_id, user_id)
        return {"success": True, "message": "Deleted", "data": res}
    except Exception as e:
        return {"success": False, "message": f"Delete failed: {e}"}


# -------------------------
# Admin endpoints
# -------------------------
class AdminLoginRequest(BaseModel):
    email: str
    password: str


@admin_router.post("/login")
async def admin_login(req: AdminLoginRequest):
    """Admin login; returns success boolean"""
    if req.email == ADMIN_EMAIL and hashlib.sha256(req.password.encode()).hexdigest() == ADMIN_PASSWORD_HASH:
        return {"success": True, "is_admin": True, "email": req.email, "message": "Admin login successful"}
    return {"success": False, "message": "Invalid admin credentials"}


@admin_router.get("/all-users")
async def admin_get_all_users(admin_email: str, admin_password: str):
    """Admin: Get all registered users"""
    if not verify_admin(admin_email, admin_password):
        return {"success": False, "message": "Unauthorized"}
    try:
        res = get_all_users()
        # Expecting get_all_users returns a dict with success OR a list
        if isinstance(res, dict) and res.get("success") is not None:
            return res
        return {"success": True, "users": res}
    except Exception as e:
        return {"success": False, "message": f"Failed to fetch users: {e}"}


@admin_router.get("/all-history")
async def admin_get_all_history(admin_email: str, admin_password: str):
    """Admin: Get all analysis history across users"""
    if not verify_admin(admin_email, admin_password):
        return {"success": False, "message": "Unauthorized"}
    try:
        res = get_all_history()
        if isinstance(res, dict) and res.get("success") is not None:
            return res
        return {"success": True, "history": res}
    except Exception as e:
        return {"success": False, "message": f"Failed to fetch history: {e}"}


@admin_router.get("/user/{user_id}")
async def admin_get_user_details(user_id: int, admin_email: str, admin_password: str):
    """Admin: Get detailed info for a specific user"""
    if not verify_admin(admin_email, admin_password):
        return {"success": False, "message": "Unauthorized"}
    try:
        res = get_user_details(user_id)
        if isinstance(res, dict) and res.get("success") is not None:
            return res
        return {"success": True, "user": res}
    except Exception as e:
        return {"success": False, "message": f"Failed to fetch user details: {e}"}


# -------------------------
# Mount routers
# -------------------------
app.include_router(auth_router)
app.include_router(analysis_router)
app.include_router(history_router)
app.include_router(admin_router)


# -------------------------
# Root healthcheck
# -------------------------
@app.get("/")
async def root():
    return {"status": "ok", "app": "Career Compass Backend"}
