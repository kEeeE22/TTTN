import torch
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
from models import SensorData

device = 'cpu'

def predict_(
    model, 
    x_samples: torch.Tensor,
    threshold: float = 0.01, 
    device: str = 'cpu', 
):
    model.eval()
    with torch.no_grad():
        x = x_samples.view(1, -1).to(device)
        x_hat = model(x)

        errs = torch.mean((x_hat - x) ** 2, dim=list(range(1, x_hat.dim())))
        preds = (errs > threshold).int()
    return preds.cpu().tolist(), errs.cpu().tolist()

def query_data(date_query: str, db):
    try:
        parsed_date = datetime.strptime(date_query, "%Y-%m-%d").date()
    except ValueError:
        return None, None   # ngày sai format

    start_datetime = datetime.combine(parsed_date, datetime.min.time())
    end_datetime = start_datetime + timedelta(days=1)

    records = (
        db.query(SensorData)
        .filter(SensorData.day == parsed_date)
        .order_by(SensorData.time)
        .all()
    )
    
    return parsed_date, records


def preprocessing(records, scaler):
    if not records:
        return None

    df = pd.DataFrame([{
        "pressure": r.pressure,
        "total_flow": r.total_flow,
        "consumption": r.consumption,
        "instant_flow": r.instant_flow,
        "day": r.day,
        "time": r.time
    } for r in records])

    df = df.sort_values(["day", "time"])

    features = ["instant_flow"]
    df[features] = scaler.transform(df[features])

    return df[features].values
