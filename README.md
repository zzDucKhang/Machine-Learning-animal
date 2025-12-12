# Iris ML + API + React Project

This project is a minimal end-to-end example:
- Trains a RandomForest on the Iris dataset (backend/src/train_model.py)
- Exposes a FastAPI endpoint to predict iris species (backend/src/api.py)
- Simple React frontend to call the API and show predictions (frontend/)

## How to run

### 2) Frontend
Move to frontend folder and install dependencies (requires Node.js):
```
cd frontend
npm install
npm start
```
Frontend will run on http://localhost:3000 and call the backend at http://127.0.0.1:8000

## Notes
- The frontend is minimal and uses fetch to call the backend /predict endpoint.
- You can customize, style, or extend it as needed.
