# import pandas as pd
# from sqlalchemy import create_engine

# # Đọc CSV
# df = pd.read_csv("D:/Huce/Coll_2/tttn/data/raw_data/Van_Dau8/luu_luong.csv")   # nếu file dạng tab-separated
# # Hoặc df = pd.read_excel("data.xlsx")

# # Chuẩn hóa tên cột
# df.columns = ["stt", "time", "datetime", "pressure", "total_flow", "consumption", "instant_flow"]


# df["datetime"] = df["datetime"].str.replace('SA', 'AM').str.replace('CH', 'PM')
# df["datetime"] = pd.to_datetime(df["datetime"], format='%d/%m/%Y %I:%M:%S %p')
# # Chuyển datetime thành kiểu datetime chuẩn
# df["timestamp"] = pd.to_datetime(df["datetime"], dayfirst=True)

# # Bỏ cột không cần
# df = df.drop(columns=["stt", "time", "datetime"])

# # Kết nối tới MySQL
# engine = create_engine("mysql+pymysql://root:123456@localhost:3306/water_leak")

# # Ghi vào DB
# df.to_sql("sensor_data", engine, if_exists="append", index=False)