from fastapi import APIRouter

from app.api.v1.routers import health, jobs, resumes

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(resumes.router)
api_router.include_router(jobs.router)
