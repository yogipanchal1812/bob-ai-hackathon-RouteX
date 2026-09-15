"""
RouteX AI Module — Standalone Application Entry Point.

Allows the AI decision-support module to run independently on its own port
(e.g., port 8001) as required by Rule 25.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai.config import ai_config
from ai.router import router as ai_router

app = FastAPI(
    title="RouteX AI Decision Support & Copilot",
    description="ChainGuard AI — Supply Chain Copilot & Recommendation Engine",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_router)


@app.get("/api/health", tags=["Health"])
def health_check():
    """Module health check."""
    return {
        "status": "healthy",
        "module": "routex-ai-copilot",
        "version": "1.0.0",
        "ibm_bob_configured": ai_config.has_ibm_credentials,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=ai_config.ai_port)
