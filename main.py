from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd

app = FastAPI()

def split_names(full_name: str):
    words = {'de','la','los','del', 'da','las'}
    original_words = str(full_name).lower().split()

    # group words
    groups = []
    i = 0
    while i < len(original_words):
        chain = []
        while i < len(original_words) and original_words[i] in words:
            chain.append(original_words[i])
            i += 1
        if i < len(original_words):
            word = " ".join(chain) + " " + original_words[i] if chain else original_words[i]
            groups.append(word.strip())
            i += 1
    # Logic for splitting into columns
    num = len(groups)
    answer = {"p_nombre":"", "s_nombre":"","t_nombre":"", "p_apellido":"", "s_apellido":""}

    if num == 2:
        answer["p_nombre"], answer["p_apellido"] = groups[0], groups[1]
    elif num == 3:
        answer["p_nombre"], answer["p_apellido"], answer["s_apellido"] = groups[0], groups[1], groups[2]
    elif num >= 4:
        answer["p_apellido"], answer["s_apellido"] = groups[-2:]
        answer["p_nombre"] = groups[0]
        answer["s_nombre"] = groups[1] if num > 3 else ""
    
    return {k: v.title() for k, v in answer.items() }

@app.get("/")
async def root():
    return {"message": "Name Splitter API is Online"}

@app.post("/split_names")
async def process_data(items: List[dict]):
    # items is the list of JSON objects from n8n
    processed_list = []
    for item in items:
        full_name = item.get("NOMBRE_COMPLETO", "")
        split_result = split_names(full_name)

        # Merge split names back into the original dictionary
        
        processed_list.append({**item, **split_result})
    
    return processed_list