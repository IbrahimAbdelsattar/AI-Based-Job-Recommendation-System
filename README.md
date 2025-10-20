# AI-Based Job Recommendation System (MVP)

This repo contains a full-stack MVP:
- Frontend: static HTML/CSS/JS (suitable for Vercel)
- Backend: FastAPI (suitable for Render/Railway)
- AI: Sentence-Transformers + FAISS (vector similarity)
- DB: SQLite (SQLAlchemy)

## Quick local setup

1. Copy `.env.example` to `.env` and edit values.
2. Create virtual env and install:

python -m venv venv
source venv/bin/activate # or venv\Scripts\activate on Windows
pip install -r requirements.txt

3. Put your dataset `JobsFE.csv` in `data/` (must contain headers: Job Id,workplace,working_mode,salary,position,job_role_and_duties,requisite_skill,offer_details).
4. Build index:

python data/build_index.py --jobs_csv data/JobsFE.csv --index_path data/jobs_index.faiss --ids_path data/job_ids.npy

5. Load jobs to DB:
python data/load_jobs_to_db.py

6. Run backend:
uvicorn app.main:app --reload

7. Serve static site: open `static/index.html` or deploy `static/` to Vercel.

## Deploy
- Frontend: deploy `static/` to Vercel (as static site).
- Backend: deploy `app/` to Render/Railway/Cloud Run; set env variables from `.env`.

    