from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from db import SessionLocal
from models import SensorData, Detection
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

@router.post("/predict", response_class=HTMLResponse)
def predict(
    request: Request,
    date_query: str = Form(...),
    db: Session = Depends(get_db)
):
    day, records = utils.query_data(date_query, db)

    results = {}

    # Nếu query_data trả về None
    if day is None:
        results[date_query] = {"status": "Ngày không hợp lệ"}

    elif not records:
        results[str(day)] = {"status": f"Không có dữ liệu ngày {day}"}

    elif len(records) < 24:
        results[str(day)] = {"status": f"Thiếu dữ liệu ({len(records)}/24 bản ghi)"}

    else:
        data = utils.preprocessing(records, scaler)
        x_tensor = torch.tensor(data, dtype=torch.float32)

        preds = utils.predict_(model, x_tensor, threshold=threshold)
        status = "Phát hiện rò rỉ" if preds == 1 else "Bình thường"
        results[str(day)] = {"status": status}

        detection = db.query(Detection).filter(Detection.day == day).first()
        if detection:
            detection.detection_result = status
        else:
            detection = Detection(day=day, detection_result=status)
            db.add(detection)
        db.commit()

    return templates.TemplateResponse("predict.html", {
        "request": request,
        "date_query": date_query,
        "results": results
    })

@router.get("/history", response_class=HTMLResponse)
def history_page(request: Request, db: Session = Depends(get_db)):
    query = (
        db.query(
            Detection.day,
            Detection.detection_result,
            Detection.created_at,
            func.avg(SensorData.pressure).label("avg_pressure"),
            func.avg(SensorData.total_flow).label("avg_flow"),
        )
        .join(SensorData, SensorData.day == Detection.day)
        .group_by(Detection.day, Detection.detection_result, Detection.created_at)
        .order_by(Detection.day.desc())
    )
    preds = query.all()

    return templates.TemplateResponse("history.html", {
        "request": request,
        "predictions": preds
    })