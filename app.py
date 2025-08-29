from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import UploadFile, File
from fastapi.staticfiles import StaticFiles

import torch
import pandas as pd
import joblib
import io

from utils.utils import predict_, preprocess_
from model.conv.kanae import Autoencoder

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

FEATURES = ['LƯU LƯỢNG TỨC THỜI 1']
checkpoint = torch.load('model/kan_18_8_lltt.pth', map_location="cpu", weights_only=False)

window_size = 24
feature_dim = 1
input_dim = window_size * feature_dim
hidden_dim = 128
latent_dim = 16

model = Autoencoder(input_dim, hidden_dim, latent_dim)
model.load_state_dict(checkpoint['model'])

threshold = checkpoint['threshold']
scaler = joblib.load("model/scaler_kan_18_8_lltt.pkl")

@app.get("/", response_class=HTMLResponse)
def form_upload(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict", response_class=HTMLResponse)
async def predict(request: Request, file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    scaled_x = preprocess_(df, FEATURES, scaler)

    prediction, error, img = predict_(model, torch.tensor(scaled_x, dtype=torch.float32), threshold=threshold, visualize=True)

    return templates.TemplateResponse("result.html", {
        "request": request,
        "result": "Phát hiện rò rỉ nước" if prediction == 1 else "Không phát hiện rò rỉ nước",
        "error": error,
        "reconstruct": img
    })