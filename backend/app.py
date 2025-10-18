from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import traceback
from main import DanceScheduler
import logging

app = FastAPI()

# Enable logging
logging.basicConfig(level=logging.INFO)

# Add error handler to ensure CORS headers are always sent
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        print(f"Error handling request: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

# Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Must be False when using allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get('/')
async def root():
    return {"ok": True, "message": "Backend is running"}
import os
import tempfile

@app.post("/generate")
async def generate_configs(
    dancers_csv: UploadFile = File(...),
    dances_csv: UploadFile = File(...)
):
    print(f"Received request to generate configs")
    print(f"Dancers file: {dancers_csv.filename}")
    print(f"Dances file: {dances_csv.filename}")
    
    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded files
            dancers_path = os.path.join(temp_dir, "dancers.csv")
            dances_path = os.path.join(temp_dir, "dances.csv")
            
            print("Saving uploaded files...")
            with open(dancers_path, "wb") as f:
                content = await dancers_csv.read()
                f.write(content)
            with open(dances_path, "wb") as f:
                content = await dances_csv.read()
                f.write(content)
            
            print("Creating scheduler...")
            scheduler = DanceScheduler.from_csv(dancers_path, dances_path)
            print("Generating configurations...")
            configs = scheduler.generate_configurations(n=5)
            print(f"Generated {len(configs)} configurations")

        if not configs:
            return {"message": "No configurations generated."}

        # Calculate satisfaction for each config and return best
        results = []
        for cfg in configs:
            score = scheduler._calculate_satisfaction(cfg)
            results.append({"satisfaction": score, "assignments": cfg})

        # Sort and return best
        results.sort(key=lambda r: r["satisfaction"], reverse=True)
        return results[0]
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
