from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from main import DanceScheduler

app = FastAPI()

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
    dancers_df = pd.read_csv(dancers_csv.file)
    dances_df = pd.read_csv(dances_csv.file)
    
    scheduler = DanceScheduler.from_dataframes(dancers_df, dances_df)
    configs = scheduler.generate_configurations(num_trials=100)
    
    if not configs:
        return {"message": "No valid configurations found."}
    
    # Return top configuration and satisfaction score
    best = configs[0]
    return {
        "satisfaction": best.satisfaction_score,
        "assignments": best.to_dict()
    }
