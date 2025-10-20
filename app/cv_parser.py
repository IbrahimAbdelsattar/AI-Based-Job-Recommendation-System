from pdfminer.high_level import extract_text
import os
from docx import Document
import re

def extract_text_from_pdf(path):
    try:
        return extract_text(path)
    except Exception as e:
        print("PDF parse error:", e)
        return ""

def extract_text_from_docx(path):
    try:
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        print("DOCX parse error:", e)
        return ""

def extract_text_from_file(path, filename):
    if filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(path)
    if filename.lower().endswith(".docx"):
        return extract_text_from_docx(path)
    # fallback
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def extract_skills_from_text(text, skill_list=None):
    if skill_list is None:
        skill_list = ["python","sql","java","machine learning","c++","excel","power bi","docker","aws","azure"]
    found = []
    t = text.lower()
    for s in skill_list:
        if s in t:
            found.append(s)
    return list(set(found))
