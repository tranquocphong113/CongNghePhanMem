import os
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# --- CẤU HÌNH KẾT NỐI ---
# Tên Server của bạn (Lưu ý: dùng 2 dấu gạch chéo \\ để Python hiểu đúng)
SERVER_NAME = 'LAPTOP-DUHHNDB7\\SQLEXPRESS01'
DATABASE_NAME = 'ProjectDB'

# Tạo chuỗi kết nối chuẩn cho SQL Server
connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    f"Trusted_Connection=yes;"  # Dùng xác thực Windows (không cần mật khẩu)
)

# Mã hóa chuỗi kết nối để dùng với SQLAlchemy
params = urllib.parse.quote_plus(connection_string)
DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"

# --- KHỞI TẠO ENGINE ---
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    # Import các model để tạo bảng
    # Lưu ý: Đảm bảo các file model này tồn tại trong thư mục models
    from database.models import (
        user,
        project,
        task,
        partner,
        feedback,
        message,
        audit_log,
    )
    
    # Lệnh này sẽ tạo các bảng trong Database nếu chưa có
    Base.metadata.create_all(bind=engine)