# backend/api/main.py

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database.config import engine, Base
from api.routes import (
    big_rocks,
    tasks,
    agent as agent_routes,
    wellness,
    capacity,
    priorizacao,
    inbox,
    analytics,
    settings,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for FastAPI app."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")
    yield
    print("👋 Shutting down Charlee...")


app = FastAPI(
    title="Charlee API",
    description="""
## 🌸 Charlee Personal Intelligence System API

**Charlee** is a personal intelligence system designed to help you manage your life effectively by:
- 🎯 Managing Big Rocks (life priorities)
- ✅ Organizing tasks and appointments
- 🤖 AI-powered task management and prioritization
- 📊 Wellness and cycle tracking (V2)
- 📈 Capacity and workload analysis (V2)

### Features

* **Big Rocks**: Manage your life priorities and focus areas
* **Tasks**: Create, update, and track tasks with deadlines
* **AI Agent**: Intelligent task analysis and recommendations
* **Wellness Tracking**: Menstrual cycle and energy patterns (V2)
* **Capacity Planning**: Workload analysis and risk detection (V2)
* **Analytics**: Insights and performance metrics (V2)

### Security

This API implements:
- Restrictive CORS policies
- Input sanitization and validation
- SQL injection protection via SQLAlchemy ORM
- XSS prevention through HTML escaping

### Version

Current version: **2.0.0**

For detailed setup instructions, see the [Backend README](../README.md).
    """,
    version="2.0.0",
    lifespan=lifespan,
    contact={
        "name": "Charlee Support",
        "url": "https://github.com/samaraCassie/Charlee",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Big Rocks",
            "description": "Manage life priorities and focus areas (Big Rocks methodology)",
        },
        {
            "name": "Tasks",
            "description": "Task management with deadlines, types, and Big Rock associations",
        },
        {
            "name": "Agent",
            "description": "AI-powered task analysis and intelligent recommendations",
        },
        {
            "name": "Wellness (V2)",
            "description": "Menstrual cycle tracking and wellness patterns",
        },
        {
            "name": "Capacity (V2)",
            "description": "Workload analysis and capacity planning",
        },
        {
            "name": "Priorização (V2)",
            "description": "Advanced task prioritization algorithms",
        },
        {
            "name": "Inbox (V2)",
            "description": "Task inbox and quick capture",
        },
        {
            "name": "Analytics (V2)",
            "description": "Performance metrics and insights",
        },
        {
            "name": "Settings (V2)",
            "description": "User preferences and configuration",
        },
    ],
)

# ========================================
# CORS CONFIGURATION - Restrictive & Secure
# ========================================
# Environment-based configuration for production flexibility
allowed_origins = [
    "http://localhost:3000",  # Vite dev server
    "http://localhost:5173",  # Vite alternative port
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# Add production frontend URL from environment if available
if frontend_url := os.getenv("FRONTEND_URL"):
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    # Specific HTTP methods only (no wildcards for security)
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    # Specific headers only (no wildcards)
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Accept-Language",
        "X-Request-ID",
    ],
    # Only expose necessary headers
    expose_headers=["Content-Type", "X-Request-ID"],
    # Cache preflight requests for 1 hour
    max_age=3600,
)

# ========================================
# ROUTERS V1
# ========================================
app.include_router(big_rocks.router, prefix="/api/v1/big-rocks", tags=["Big Rocks"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(agent_routes.router, prefix="/api/v1/agent", tags=["Agent"])

# ========================================
# ROUTERS V2
# ========================================
app.include_router(wellness.router, prefix="/api/v2/wellness", tags=["Wellness (V2)"])
app.include_router(capacity.router, prefix="/api/v2/capacity", tags=["Capacity (V2)"])
app.include_router(priorizacao.router, prefix="/api/v2/priorizacao", tags=["Priorização (V2)"])
app.include_router(inbox.router, prefix="/api/v2/inbox", tags=["Inbox (V2)"])
app.include_router(analytics.router, prefix="/api/v2/analytics", tags=["Analytics (V2)"])
app.include_router(settings.router, prefix="/api/v2/settings", tags=["Settings (V2)"])


# ========================================
# BASIC ENDPOINTS
# ========================================
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "🌸 Charlee API - Sistema de Inteligência Pessoal",
        "version": "2.0.0",
        "status": "online",
        "cors": "enabled",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint with database connectivity."""
    from fastapi import status as http_status
    from sqlalchemy import text
    from database.config import SessionLocal
    from datetime import datetime

    health_status = {
        "service": "charlee-backend",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "healthy",
        "checks": {}
    }

    # Check database connection
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }

    # Check if critical tables exist
    try:
        db = SessionLocal()
        db.execute(text("SELECT COUNT(*) FROM big_rocks"))
        db.execute(text("SELECT COUNT(*) FROM tasks"))
        db.close()
        health_status["checks"]["tables"] = {
            "status": "healthy",
            "message": "Critical tables exist"
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["checks"]["tables"] = {
            "status": "unhealthy",
            "message": f"Tables check failed: {str(e)}"
        }

    # Environment info
    health_status["environment"] = {
        "python_version": os.sys.version.split()[0],
        "debug_mode": os.getenv("DEBUG", "false").lower() == "true"
    }

    # Return appropriate HTTP status code
    if health_status["status"] == "unhealthy":
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status
        )

    return health_status
