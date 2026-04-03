from fastapi import FastAPI
from database import Base, engine

from models import User, Record, Role, Department, Category
from routes import user
from routes import auth
from routes import record
from routes import dashboard

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "Backend running"}

# To keep Render Server alive, we can add a simple health check endpoint
@app.get("/health")
def Render_Service():
    return {"status": "ok"}

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(record.router)
app.include_router(dashboard.router)