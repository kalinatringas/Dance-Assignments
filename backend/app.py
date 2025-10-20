from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import traceback
from main import DanceScheduler
import logging
import io
import contextlib

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

        # Calculate satisfaction for each config, capture the human-readable report text,
        # and return structured data + the report text so the frontend can display it.
        results = []
        for i, cfg in enumerate(configs, start=1):
            score = scheduler._calculate_satisfaction(cfg)

            violations = scheduler._return_violations(cfg, config_num=i)

            # Get a human-readable report string directly from scheduler
            try:
                report_text = scheduler.configuration_report(cfg, config_num=i)
            except Exception:
                report_text = "(Failed to generate report_text)\n" + traceback.format_exc()

            # Build dance -> [dancers] mapping for easier display on frontend
            dance_map = {}
            from collections import defaultdict as _dd
            tmp = _dd(list)
            for dancer, dances in cfg.items():
                for dance in dances:
                    tmp[dance].append(dancer)
            # sort dancer lists for determinism
            for k in tmp:
                tmp[k] = sorted(tmp[k])
            #what i need is something that captures violations and returns 
            results.append({
                "satisfaction": score,
                "assignments": cfg,  # dancer -> [dances], kept for compatibility
                "assignments_by_dance": dict(tmp),
                "violations" : violations,
                "report_text": report_text
            })

        # Sort and return results by satisfaction (best first)
        results.sort(key=lambda r: r["satisfaction"], reverse=True)
        return results
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
