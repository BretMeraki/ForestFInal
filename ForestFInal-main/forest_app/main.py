# This is a compatibility file to ensure the app loads correctly in deployment
# It simply re-exports the FastAPI app from the core.main module

from forest_app.core.main import app

# Make sure to export the app variable for ASGI servers to find
__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(
        "forest_app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("APP_ENV", "development") == "development",
    )
