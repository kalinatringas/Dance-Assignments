from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import Any

from main import DanceScheduler

app = FastAPI()


@app.get('/')
async def root():
    return {"ok": True, "message": "Backend is running"}

# Allow frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate")
async def generate_configs(
    dancers_csv: UploadFile = File(...),
    dances_csv: UploadFile = File(...)
):
    try:
        dancers_df = pd.read_csv(dancers_csv.file)
        dances_df = pd.read_csv(dances_csv.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSVs: {e}")

    scheduler = DanceScheduler.from_dataframes(dancers_df, dances_df)
    configs = scheduler.generate_configurations(n=5, num_trials=100)

    if not configs:
        return {"message": "No configurations generated."}

    # configs are plain dicts of assignments; calculate satisfaction for each and return best
    results = []
    for cfg in configs:
        score = scheduler._calculate_satisfaction(cfg)
        results.append({"satisfaction": score, "assignments": cfg})

    # sort and return best
    results.sort(key=lambda r: r["satisfaction"], reverse=True)
    return results[0]
