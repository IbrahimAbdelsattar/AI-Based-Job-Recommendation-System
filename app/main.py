from fastapi import FastAPI, Request, Depends, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from . import models, db, recommender, cv_parser, auth
from .schemas import StructuredRequest, ChatRequest
import os, shutil, numpy as np

app = FastAPI(title="Neuronix AI Job Recommendation")

models.Base.metadata.create_all(bind=db.engine)

RECOMMENDER = None
def get_recommender():
    global RECOMMENDER
    if RECOMMENDER is None:
        RECOMMENDER = recommender.Recommender()
    return RECOMMENDER

@app.post("/recommend/structured")
async def recommend_structured(request: Request, session: Session = Depends(db.SessionLocal)):
    data = await request.json()
    # safe extraction with defaults
    position = data.get("position", "")
    skills = data.get("skills", "")
    working_mode = data.get("working_mode", "")
    salary = data.get("salary", 0)
    workplace = data.get("workplace", "")
    offer_details = data.get("offer_details", "")
    experience = data.get("experience_level", "")
    # build query
    q = f"Position: {position}. Skills: {skills}. Mode: {working_mode}. Salary: {salary}. Workplace: {workplace}. Offer: {offer_details}."
    r = get_recommender()
    results = r.retrieve(q, top_k=20)
    # fetch job metadata
    job_ids = [res[0] for res in results]
    jobs = session.query(models.Job).filter(models.Job.job_id.in_(job_ids)).all()
    job_map = {j.job_id: j for j in jobs}
    out = []
    for jid, sim in results:
        job = job_map.get(str(jid))
        if not job:
            continue
        # compute skill ratio
        required = (job.skills or "")
        req_skills = [s.strip().lower() for s in required.split(",") if s.strip()]
        user_skills = [s.strip().lower() for s in (skills or "").split(",") if s.strip()]
        match_count = sum(1 for s in req_skills if s in user_skills) if req_skills else 0
        skill_ratio = (match_count / len(req_skills)) if req_skills else 0.0
        # salary score simple
        salary_score = 1.0 if (job.salary and str(salary) in str(job.salary)) else 0.0
        # recency_score placeholder
        recency_score = 0.5
        match_score = recommender.compute_match_score(similarity=sim, skill_ratio=skill_ratio, salary_score=salary_score, experience_score=0.0, recency_score=recency_score)
        out.append({
            "id": job.id,
            "job_id": job.job_id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description,
            "skills": job.skills,
            "salary": job.salary,
            "match_score": round(match_score * 100, 2),
            "link": job.extra.get("url") if job.extra and job.extra.get("url") else None
        })
    return JSONResponse(content={"results": out})

@app.post("/recommend/chat")
async def recommend_chat(payload: ChatRequest, session: Session = Depends(db.SessionLocal)):
    r = get_recommender()
    results = r.retrieve(payload.text, top_k=20)
    job_ids = [res[0] for res in results]
    jobs = session.query(models.Job).filter(models.Job.job_id.in_(job_ids)).all()
    job_map = {j.job_id: j for j in jobs}
    out = []
    for jid, sim in results:
        job = job_map.get(str(jid))
        if not job:
            continue
        skill_ratio = 0.0
        match_score = recommender.compute_match_score(similarity=sim, skill_ratio=skill_ratio)
        out.append({
            "id": job.id,
            "job_id": job.job_id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description,
            "skills": job.skills,
            "salary": job.salary,
            "match_score": round(match_score * 100, 2),
            "link": job.extra.get("url") if job.extra and job.extra.get("url") else None
        })
    return JSONResponse(content={"results": out})

@app.post("/upload_cv")
async def upload_cv(file: UploadFile = File(...), session: Session = Depends(db.SessionLocal)):
    tmp_path = f"/tmp/{file.filename}"
    with open(tmp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    text = cv_parser.extract_text_from_file(tmp_path, file.filename)
    skills = cv_parser.extract_skills_from_text(text)
    query = f"Extracted skills: {', '.join(skills)}. Resume text: {text[:800]}"
    r = get_recommender()
    results = r.retrieve(query, top_k=20)
    job_ids = [res[0] for res in results]
    jobs = session.query(models.Job).filter(models.Job.job_id.in_(job_ids)).all()
    job_map = {j.job_id: j for j in jobs}
    out = []
    for jid, sim in results:
        job = job_map.get(str(jid))
        if not job:
            continue
        match_score = recommender.compute_match_score(similarity=sim)
        out.append({
            "id": job.id,
            "job_id": job.job_id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description,
            "skills": job.skills,
            "salary": job.salary,
            "match_score": round(match_score * 100, 2),
            "link": job.extra.get("url") if job.extra and job.extra.get("url") else None
        })
    # remove temp
    try:
        os.remove(tmp_path)
    except: pass
    return JSONResponse(content={"results": out})

# Simple Auth routes (signup/login)
from fastapi import Body
from .schemas import UserCreate
from .auth import get_password_hash, create_access_token, verify_password
from sqlalchemy.exc import IntegrityError

@app.post("/auth/signup")
def signup(user: UserCreate):
    dbs = db.SessionLocal()
    from .models import User
    hashed = get_password_hash(user.password)
    u = User(email=user.email, hashed_password=hashed, full_name=user.full_name)
    try:
        dbs.add(u)
        dbs.commit()
        dbs.refresh(u)
    except IntegrityError:
        dbs.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    token = create_access_token(str(u.id))
    return {"access_token": token, "token_type": "bearer"}

@app.post("/auth/login")
def login(data: UserCreate):
    dbs = db.SessionLocal()
    from .models import User
    user = dbs.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(str(user.id))
    return {"access_token": token, "token_type": "bearer"}
