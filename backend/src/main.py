"""
Main entry point for Klassa KRT classification API.
"""

import os
import uvicorn
from dotenv import load_dotenv
from klassa.api.app import create_app

# Load environment variables
load_dotenv()

# Create FastAPI app
app = create_app()


if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
