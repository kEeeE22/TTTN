from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from db import SessionLocal
from models import SensorData
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta

import torch
import joblib

from utils import utils
from checkpoint.conv.kanae import Autoencoder

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

templates = Jinja2Templates(directory="templates") 
#model
checkpoint = torch.load('checkpoint/kan_18_8_lltt.pth', map_location="cpu", weights_only=False)
window_size = 24
feature_dim = 1
input_dim = window_size * feature_dim
hidden_dim = 128
latent_dim = 16
model = Autoencoder(input_dim, hidden_dim, latent_dim)
model.load_state_dict(checkpoint['model'])
model.eval()
threshold = checkpoint['threshold']
#scaler
scaler = joblib.load("checkpoint/scaler_kan_18_8_lltt.pkl")

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/predict/", response_class=HTMLResponse)
def predict(request: Request,
    date_query: str = Form(...),
    db: Session = Depends(get_db)):

    #preprocess
    records, start_date, end_date = utils.query_data(date_query, db)

    scaled_data = utils.preprocessing(records=records, start_date=start_date, end_date=end_date, scaler=scaler)
    results = {}
    for day, data in scaled_data.items():
        if isinstance(data, str) and data == "không có":
            results[day] = {"status": "Không có dữ liệu"}
        else:
            x_tensor = torch.tensor(data, dtype=torch.float32)
            preds = utils.predict_(model, x_tensor, threshold=threshold)
            status = "Phát hiện rò rỉ" if preds == 1 else "Bình thường"
            results[str(day)] = {"status": status}

    return templates.TemplateResponse("predict.html", {
        "request": request,
        "date_query": date_query,
        "results": results
    })