from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.db import init_db
from database.seed import seed_system_admin
from routers import feedback, messages, partners, projects, tasks, users

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_system_admin()
    
    yield  
    

app = FastAPI(
    title="FUSION - Multi-Enterprise IT Project Maintenance & Development Platform",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      
    allow_credentials=True,
    allow_methods=["*"],      
    allow_headers=["*"],      
)

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(partners.router)
app.include_router(feedback.router)
app.include_router(messages.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)