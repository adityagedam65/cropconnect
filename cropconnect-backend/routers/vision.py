"""Authenticated Camera 1 crop-image endpoint."""

from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter, Cookie, Header, HTTPException, Request

from crop_analysis import CropAnalyzer, build_crop_analyzer
from vision_models.detector import ModelUnavailableError
from services.auth_service import require_auth_owner

AUTH_COOKIE_NAME = "cropconnect_auth"
router = APIRouter()


@lru_cache(maxsize=1)
def get_crop_analyzer() -> CropAnalyzer:
    """Build the detector-plus-classifier flow once per application process."""
    return build_crop_analyzer()


@router.post("/api/vision/analyze")
async def analyze_crop_image(
    request: Request,
    authorization: str | None = Header(default=None),
    auth_cookie: str | None = Cookie(default=None, alias=AUTH_COOKIE_NAME),
):
    require_auth_owner(authorization, auth_cookie)
    if not (request.headers.get("content-type") or "").startswith("image/"):
        raise HTTPException(status_code=415, detail="Upload an image file")
    content = await request.body()
    if not content:
        raise HTTPException(status_code=422, detail="The uploaded image is empty")
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image must be 10 MB or smaller")
    try:
        import cv2
        import numpy as np

        decoded = cv2.imdecode(np.frombuffer(content, dtype=np.uint8), cv2.IMREAD_COLOR)
    except (ImportError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="Please upload a proper crop or leaf photo.") from exc
    if decoded is None:
        raise HTTPException(status_code=422, detail="Please upload a proper crop or leaf photo.")
    try:
        return get_crop_analyzer().analyze(content)
    except ModelUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        request.app.state.logger.exception("Crop image analysis failed") if hasattr(request.app.state, "logger") else None
        raise HTTPException(status_code=422, detail="The image could not be analyzed") from exc
