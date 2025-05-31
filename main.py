from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
from datetime import datetime
import os

from app.database.db import init_db, get_db, engine
from app.routes import call_routes, webhook_routes, admin_routes
from app.models.database import Base
from app.utils.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Voice Agent System",
    description="A Python-based AI voice assistant that handles inbound and outbound calls for customer support",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(call_routes.router)
app.include_router(webhook_routes.router)
app.include_router(admin_routes.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting AI Voice Agent System")
    await init_db()
    logger.info("Database initialized")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down AI Voice Agent System")

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint for health checking
    """
    return {"message": "AI Voice Agent System is running", "status": "ok", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)