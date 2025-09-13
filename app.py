from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import controllers
from db import Base, engine
import models

app = FastAPI()
Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(controllers.router)
