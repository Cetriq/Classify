"""
FastAPI application for KRT classification API.
Implements the OpenAPI spec from spec.md section 12.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ..core.classifier import Classifier
from ..models.classification import ClassificationInput, ClassificationOutput


# Global classifier instance
classifier: Classifier = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    global classifier
    # Startup
    classifier = Classifier()
    yield
    # Shutdown
    classifier = None


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title="Klassa KRT Classification API",
        description="AI-powered information classification system for Swedish public sector",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS configuration
    if os.getenv("ENABLE_CORS", "true").lower() == "true":
        allowed_origins = os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:3000,http://localhost:8000"
        ).split(",")

        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": "Klassa KRT Classification API",
            "version": "1.0.0",
            "status": "operational",
            "endpoints": {
                "classify": "/classify",
                "health": "/health",
                "docs": "/docs",
            }
        }

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "classifier": "ready" if classifier else "not initialized"
        }

    @app.post("/classify", response_model=ClassificationOutput)
    async def classify_endpoint(input_data: ClassificationInput) -> ClassificationOutput:
        """
        Classify an information system/process.

        Performs KRT (Konfidentialitet, Riktighet, Tillgänglighet) classification
        and determines LoA (Level of Assurance) based on GDPR, OSL, and Swedish
        municipal requirements.

        **Privacy by Design**: This endpoint only receives metadata tags,
        never raw personal data.

        Args:
            input_data: Classification input with metadata

        Returns:
            Complete classification with K/R/T/LoA levels, rationale,
            confidence scores, and suggested security measures.
        """
        if not classifier:
            raise HTTPException(
                status_code=503,
                detail="Classifier not initialized. Please try again."
            )

        try:
            result = classifier.classify(input_data)
            return result

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Classification error: {str(e)}"
            )

    @app.post("/classify/batch", response_model=list[ClassificationOutput])
    async def classify_batch_endpoint(
        inputs: list[ClassificationInput]
    ) -> list[ClassificationOutput]:
        """
        Classify multiple objects in batch.

        Args:
            inputs: List of classification inputs

        Returns:
            List of classification outputs
        """
        if not classifier:
            raise HTTPException(
                status_code=503,
                detail="Classifier not initialized. Please try again."
            )

        if len(inputs) > 100:
            raise HTTPException(
                status_code=400,
                detail="Batch size limit: 100 items"
            )

        try:
            results = classifier.classify_batch(inputs)
            return results

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Batch classification error: {str(e)}"
            )

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Global exception handler."""
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(exc)}"}
        )

    return app
