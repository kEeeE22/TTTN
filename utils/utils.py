import torch
import matplotlib.pyplot as plt
import io, base64
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
from models import SensorData

device = 'cpu'

def predict_(
    model, 
    x_samples: torch.Tensor,
    threshold: float = 0.01, 
    flat: bool = True, 
    device: str = 'cpu', 
):
    model.eval()
    with torch.no_grad():
        x = x_samples.view(1, -1).to(device)
        x_hat = model(x)

        errs = torch.mean((x_hat - x) ** 2, dim=list(range(1, x_hat.dim())))
        preds = (errs > threshold).int()
    return preds.cpu().tolist(), errs.cpu().tolist()


def query_data(date_query, db):
    try:
        parsed_date = datetime.strptime(date_query, "%Y-%m-%d").date()
    except ValueError:
        return {"error": "Ngày không hợp lệ"}

    start_date = parsed_date - timedelta(days=2)
    end_date = parsed_date + timedelta(days=3)

    records = db.query(SensorData).filter(
        SensorData.timestamp >= datetime.combine(start_date, datetime.min.time()),
        SensorData.timestamp < datetime.combine(end_date, datetime.min.time())
    ).all()

    return records, start_date, end_date 

def preprocessing(records, start_date, end_date, scaler):
    if not records:
        return {}

    df = pd.DataFrame([{
        "pressure": r.pressure,
        "total_flow": r.total_flow,
        "consumption": r.consumption,
        "instant_flow": r.instant_flow,
        "timestamp": r.timestamp
    } for r in records])

    df = df.sort_values("timestamp")

    features = ["instant_flow"]
    df[features] = scaler.transform(df[features])

    grouped = defaultdict(list)
    for _, row in df.iterrows():
        ts = row["timestamp"]
        if ts.time() == ts.min.time():
            day = (ts - timedelta(days=1)).date()
        else:
            day = ts.date()
        grouped[day].append(row[features].values)

    result = {}
    current = start_date
    while current <= end_date:
        if current in grouped:
            result[current] = pd.DataFrame(grouped[current], columns=features).values
        else:
            result[current] = "không có"
        current += timedelta(days=1)

    return result
