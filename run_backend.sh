#!/bin/bash
# Train model and run FastAPI
python3 backend/src/train_model.py
uvicorn backend.src.api:app --reload --host 0.0.0.0 --port 8000
