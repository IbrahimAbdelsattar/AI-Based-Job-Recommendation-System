import pandas as pd
from app import db, models
import os
from sqlalchemy.exc import IntegrityError

CSV = os.path.join(os.path.dirname(__file__), "JobsFE.csv")
df = pd.read_csv(CSV, encoding='utf-8', on_bad_lines='skip')

session = db.SessionLocal()
for _, row in df.iterrows():
    job = models.Job(
        job_id=str(row.get('Job Id','')).strip(),
        title=str(row.get('position','')).strip(),
        company=str(row.get('workplace','')).strip(),
        location=str(row.get('working_mode','')).strip(),
        description=str(row.get('job_role_and_duties','')).strip(),
        skills=str(row.get('requisite_skill','')).strip(),
        salary=str(row.get('salary','')).strip(),
        working_mode=str(row.get('working_mode','')).strip(),
        extra={"offer_details": str(row.get('offer_details','')).strip(), "url": str(row.get('url','')).strip() if 'url' in row else None}
    )
    try:
        session.merge(job)
        session.commit()
    except IntegrityError:
        session.rollback()
session.close()
print("Jobs loaded into DB.")
