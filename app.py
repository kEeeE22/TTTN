from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import controllers

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(controllers.router)
