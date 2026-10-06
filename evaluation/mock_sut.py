"""
Standalone Mock System Under Test (SUT) server implementing the FastAPI endpoints,
scoring rules, RBAC, prompt injection scanner, and audit log persistence as specified in Section 2 & 7.
"""

import os
import re
import json
import time
import datetime
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Header, HTTPException, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="Resume Screening AI SUT")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_HTML = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend/index.html"))

DATA_DIR = os.path.join(os.path.dirname(__file__), "sut_data")
EVAL_DIR = os.path.join(DATA_DIR, "evaluations")
os.makedirs(EVAL_DIR, exist_ok=True)

# Mock tokens
VALID_TOKENS = {
    "recruiter_token_123": {"user": "recruiter_user", "role": "recruiter"},
    "admin_token_456": {"user": "admin_user", "role": "admin"},
}

INJECTION_PATTERNS = [
    r"recommend\s+advance",
    r"ignore\s+previous\s+instructions",
    r"score\s*=\s*100",
    r"grant\s+full\s+access",
    r"system\s*:\s*override",
    r"\[hidden_text\]"
]


class LoginRequest(BaseModel):
    username: str
    password: str


class EvalRequest(BaseModel):
    jd_text: str
    resume_text: str


class EvalResult(BaseModel):
    fit_score: int
    recommendation: str
    matched_skills: List[str]
    missing_skills: List[str]
    justification: str
    injection_flags: List[str]


def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, str]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authentication token")
    token = authorization.replace("Bearer ", "").strip()
    if token == "expired_token":
        raise HTTPException(status_code=401, detail="Token has expired")
    if token == "tampered_token":
        raise HTTPException(status_code=401, detail="Token signature invalid")
    if token not in VALID_TOKENS:
        raise HTTPException(status_code=401, detail="Unauthorized token")
    return VALID_TOKENS[token]


def require_admin(user: Dict[str, str] = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: Admin access required")
    return user


@app.get("/")
def read_root():
    if os.path.exists(FRONTEND_HTML):
        return FileResponse(FRONTEND_HTML)
    return {"message": "Resume Screening AI SUT"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/login")
def login(req: LoginRequest):
    if req.username == "admin" and req.password == "adminpass":
        return {"access_token": "admin_token_456", "token_type": "bearer", "role": "admin"}
    elif req.username == "recruiter" and req.password == "recruiterpass":
        return {"access_token": "recruiter_token_123", "token_type": "bearer", "role": "recruiter"}
    raise HTTPException(status_code=401, detail="Invalid username or password")


@app.post("/upload-resume")
def upload_resume(file: UploadFile = File(...), user: Dict[str, str] = Depends(get_current_user)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".txt", ".md", ".pdf", ".docx"]:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
    content = file.file.read().decode("utf-8", errors="ignore")
    return {"filename": file.filename, "resume_text": content}


def calculate_score(jd_text: str, resume_text: str) -> EvalResult:
    # Scan for prompt injections
    injection_flags = []
    combined_text = (jd_text + " " + resume_text).lower()
    for pat in INJECTION_PATTERNS:
        if re.search(pat, combined_text):
            injection_flags.append(f"Detected injection pattern: {pat}")

    # Skill extraction simulation
    common_skills = ["Python", "SQL", "FastAPI", "Docker", "AWS", "React", "PyTest", "Machine Learning", "Communication"]
    req_skills = [s for s in common_skills if s.lower() in jd_text.lower()]
    if not req_skills:
        req_skills = ["Python", "SQL", "Communication"]

    res_lower = resume_text.lower()
    matched = [s for s in req_skills if s.lower() in res_lower]
    missing = [s for s in req_skills if s.lower() not in res_lower]

    match_ratio = len(matched) / len(req_skills) if req_skills else 0.0
    base_score = int(match_ratio * 90) + (10 if len(matched) > 2 else 0)

    # Hard Caps verification (Section 2.2)
    applied_cap = 100
    if len(missing) >= 3:
        applied_cap = min(applied_cap, 65)
    if "domain mismatch" in res_lower or "unrelated domain" in res_lower:
        applied_cap = min(applied_cap, 70)
    if "last performed: 2020" in res_lower or "last performed >=2 years ago" in res_lower or "inactive since 2022" in res_lower:
        applied_cap = min(applied_cap, 75)
    if match_ratio < 0.5:
        applied_cap = min(applied_cap, 50)

    final_score = min(base_score, applied_cap)

    if final_score >= 80:
        rec = "Advance"
    elif final_score >= 50:
        rec = "Hold"
    else:
        rec = "Reject"

    justification = f"Candidate matched {len(matched)}/{len(req_skills)} required skills ({', '.join(matched) or 'None'}). Missing: {', '.join(missing) or 'None'}."
    if applied_cap < 100:
        justification += f" Score capped at {applied_cap} due to business rules."

    return EvalResult(
        fit_score=final_score,
        recommendation=rec,
        matched_skills=matched,
        missing_skills=missing,
        justification=justification,
        injection_flags=injection_flags
    )


@app.post("/evaluate")
def evaluate(req: EvalRequest, user: Dict[str, str] = Depends(get_current_user)):
    result = calculate_score(req.jd_text, req.resume_text)
    eval_id = f"eval_{int(time.time() * 1000)}"
    eval_folder = os.path.join(EVAL_DIR, eval_id)
    os.makedirs(eval_folder, exist_ok=True)

    with open(os.path.join(eval_folder, "jd.txt"), "w", encoding="utf-8") as f:
        f.write(req.jd_text)
    with open(os.path.join(eval_folder, "resume.txt"), "w", encoding="utf-8") as f:
        f.write(req.resume_text)

    audit_record = {
        "id": eval_id,
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
        "performed_by": user["user"],
        "model": "gemini-2.5-flash",
        "prompt_version": "v1.0",
        "extraction": {
            "matched_skills": result.matched_skills,
            "missing_skills": result.missing_skills
        },
        "result": result.dict()
    }
    with open(os.path.join(eval_folder, "audit.json"), "w", encoding="utf-8") as f:
        json.dump(audit_record, f, indent=2)

    return result.dict()


@app.get("/evaluations")
def list_evaluations(user: Dict[str, str] = Depends(require_admin)):
    evals = []
    if os.path.exists(EVAL_DIR):
        for name in os.listdir(EVAL_DIR):
            audit_path = os.path.join(EVAL_DIR, name, "audit.json")
            if os.path.exists(audit_path):
                with open(audit_path, "r", encoding="utf-8") as f:
                    evals.append(json.load(f))
    return evals


@app.get("/evaluations/{eval_id}")
def get_evaluation(eval_id: str, user: Dict[str, str] = Depends(require_admin)):
    if ".." in eval_id or "/" in eval_id or "\\" in eval_id:
        raise HTTPException(status_code=400, detail="Path traversal detected")
    audit_path = os.path.join(EVAL_DIR, eval_id, "audit.json")
    if not os.path.exists(audit_path):
        raise HTTPException(status_code=404, detail="Evaluation not found")
    with open(audit_path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
