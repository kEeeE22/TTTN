from sqlalchemy import Column, Integer, Float, DateTime
from db import Base

class SensorData(Base):
    __tablename__ = "sensor_data"

    # id = Column(Integer, primary_key=True, index=True)         
    timestamp = Column(DateTime, primary_key=True, index=True)     # Ngày + giờ
    pressure = Column(Float)                         # ÁP LỰC 1
    total_flow = Column(Float)                       # TỔNG LƯU LƯỢNG 1
    consumption = Column(Float)                      # Tiêu thụ
    instant_flow = Column(Float)                     # LƯU LƯỢNG TỨC THỜI 1
    