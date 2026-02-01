from contextlib import asynccontextmanager
from fastapi import FastAPI
# 1. Thêm thư viện CORS vào đây
from fastapi.middleware.cors import CORSMiddleware

from database.db import init_db
from database.seed import seed_system_admin
from routers import feedback, messages, partners, projects, tasks, users

# --- 1. Định nghĩa Lifespan (Vòng đời ứng dụng) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # [STARTUP] Code chạy khi server khởi động
    init_db()
    seed_system_admin()
    
    yield  # Điểm phân cách giữa khởi động và tắt
    
    # [SHUTDOWN] Code chạy khi server tắt

# --- 2. Khởi tạo app với tham số lifespan ---
app = FastAPI(
    title="FUSION - Multi-Enterprise IT Project Maintenance & Development Platform",
    lifespan=lifespan
)

# --- 3. CẤU HÌNH CORS (QUAN TRỌNG ĐỂ FRONTEND KẾT NỐI ĐƯỢC) ---
# Đoạn này cho phép mọi nguồn (origins=["*"]) đều có thể gọi API này.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Cho phép tất cả các trang web kết nối (Frontend chạy port nào cũng được)
    allow_credentials=True,
    allow_methods=["*"],      # Cho phép tất cả các phương thức (GET, POST, PUT, DELETE...)
    allow_headers=["*"],      # Cho phép tất cả các headers
)

# --- 4. Đăng ký các Routers ---
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(partners.router)
app.include_router(feedback.router)
app.include_router(messages.router)

if __name__ == "__main__":
    import uvicorn
    # Chạy server uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)