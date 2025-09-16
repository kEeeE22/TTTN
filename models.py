from sqlalchemy import Column, Integer, Float, String, TIMESTAMP, func, Date, Time
from db import Base

class SensorData(Base):
    __tablename__ = "sensor_data"
       
    day = Column(Date, primary_key=True, index=True)
    time = Column(Time, primary_key=True, index=True)
    pressure = Column(Float)                        
    total_flow = Column(Float)                        
    consumption = Column(Float)                            
    instant_flow = Column(Float)
    
class Detection(Base):
    __tablename__ = "detections"

    day = Column(Date, primary_key=True, index=True)
    detection_result = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())