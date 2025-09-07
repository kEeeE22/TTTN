import pandas as pd
from sqlalchemy import create_engine

df = pd.read_csv("/luu_luong.csv")

df.columns = ["stt", "time", "datetime", "pressure", "total_flow", "consumption", "instant_flow"]

df["datetime"] = df["datetime"].str.replace('SA', 'AM').str.replace('CH', 'PM')
df["datetime"] = pd.to_datetime(df["datetime"], format='%d/%m/%Y %I:%M:%S %p')

df["timestamp"] = pd.to_datetime(df["datetime"], dayfirst=True)

df = df.drop(columns=["stt", "time", "datetime"])

engine = create_engine("mysql+pymysql://root:123456@localhost:3306/water_leak")

df.to_sql("sensor_data", engine, if_exists="append", index=False)