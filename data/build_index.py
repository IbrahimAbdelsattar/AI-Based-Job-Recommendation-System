import argparse
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import os

def build_index(jobs_csv, index_path, ids_path, model_name='paraphrase-multilingual-MiniLM-L12-v2'):
    df = pd.read_csv(jobs_csv, encoding='utf-8', on_bad_lines='skip')
    # generate combined text
    df['all_text'] = (
        df.get('position','').fillna('') + '. ' +
        df.get('job_role_and_duties','').fillna('') + '. Skills: ' +
        df.get('requisite_skill','').fillna('') + '. Offer: ' +
        df.get('offer_details','').fillna('') + '. Workplace: ' +
        df.get('workplace','').fillna('') + '. Mode: ' +
        df.get('working_mode','').fillna('')
    )
    texts = df['all_text'].astype(str).tolist()
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    faiss.normalize_L2(embeddings)
    d = embeddings.shape[1]
    index = faiss.IndexFlatIP(d)
    index.add(embeddings)
    faiss.write_index(index, index_path)
    ids = df['Job Id'].astype(str).values
    np.save(ids_path, ids)
    print(f"Index saved to {index_path}, ids saved to {ids_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--jobs_csv', required=True)
    parser.add_argument('--index_path', required=True)
    parser.add_argument('--ids_path', required=True)
    args = parser.parse_args()
    build_index(args.jobs_csv, args.index_path, args.ids_path)
