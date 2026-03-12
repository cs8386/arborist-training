"""Training CRUD and slide generation API."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.models.database import get_db
from app.models import training as training_db
from app.auth_deps import verify_token
from app.seed_trainings import add_sample_trainings
from app.services.claude_service import generate_slide_content
from app.services.slides_service import create_presentation
from app.utils.google_auth import dict_to_credentials
from app.linked_google import get_credentials

router = APIRouter(prefix="/api/trainings", tags=["trainings"], dependencies=[Depends(verify_token)])


class TrainingCreate(BaseModel):
    title: str
    description: str = ""
    standard: str
    category: str = ""
    format: str = "standard"  # "standard" or "deep_dive"
    topics: list[str] = []


class TrainingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    format: Optional[str] = None
    status: Optional[str] = None
    covered_at: Optional[str] = None  # ISO timestamp when marked "went over", null to unmark


class GenerateSlidesRequest(BaseModel):
    google_credentials: dict | None = None  # Optional when using server-linked Google


class MarkCoveredRequest(BaseModel):
    covered: bool = True


@router.post("/{training_id}/mark-covered")
def mark_training_covered(training_id: int, body: MarkCoveredRequest, conn=Depends(get_db)):
    """Mark a training as covered (went over) or unmark it."""
    t = training_db.get_by_id(conn, training_id)
    if not t:
        raise HTTPException(status_code=404, detail="Training not found")
    from datetime import datetime, timezone
    covered_at = datetime.now(timezone.utc).isoformat() if body.covered else None
    return training_db.update(conn, training_id, covered_at=covered_at)


@router.post("/seed")
def load_sample_trainings(conn=Depends(get_db)):
    """Add pre-built sample trainings (ISA, ANSI Z133, OSHA Crane)."""
    added = add_sample_trainings(conn)
    return {"added": added, "message": f"Added {added} sample trainings"}


@router.get("")
def list_trainings(conn=Depends(get_db)):
    try:
        return training_db.get_all(conn)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
def create_training(data: TrainingCreate, conn=Depends(get_db)):
    topics = ",".join(data.topics) if data.topics else ""
    return training_db.create(conn, data.title, data.description, data.standard, topics, data.category, data.format)


@router.get("/{training_id}")
def get_training(training_id: int, conn=Depends(get_db)):
    t = training_db.get_by_id(conn, training_id)
    if not t:
        raise HTTPException(status_code=404, detail="Training not found")
    return t


@router.patch("/{training_id}")
def update_training(training_id: int, data: TrainingUpdate, conn=Depends(get_db)):
    t = training_db.get_by_id(conn, training_id)
    if not t:
        raise HTTPException(status_code=404, detail="Training not found")
    kwargs = {k: v for k, v in data.model_dump().items() if v is not None}
    return training_db.update(conn, training_id, **kwargs)


@router.delete("/{training_id}")
def delete_training(training_id: int, conn=Depends(get_db)):
    t = training_db.get_by_id(conn, training_id)
    if not t:
        raise HTTPException(status_code=404, detail="Training not found")
    training_db.delete(conn, training_id)
    return {"ok": True}


@router.post("/{training_id}/generate-slides")
async def generate_and_create_slides(
    training_id: int,
    req: GenerateSlidesRequest,
    conn=Depends(get_db),
):
    training = training_db.get_by_id(conn, training_id)
    if not training:
        raise HTTPException(status_code=404, detail="Training not found")

    try:
        slides_content = await generate_slide_content(
            title=training["title"],
            description=training.get("description", "") or "",
            standard=training["standard"],
            topics=training.get("topics") or [],
            format=training.get("format", "standard"),
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Claude error: {str(e)}")

    creds_dict = None
    if req.google_credentials:
        creds = dict_to_credentials(req.google_credentials)
        creds_dict = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": list(creds.scopes),
        }
    else:
        creds_dict = get_credentials()
    if not creds_dict:
        raise HTTPException(
            status_code=400,
            detail="Google account not linked. Owner must link Google first at Connect Google → Link Account.",
        )
    try:
        presentation_id, slides_url = create_presentation(
            credentials=creds_dict,
            title=training["title"],
            slides_content=slides_content,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google Slides error: {str(e)}")

    updated = training_db.update(
        conn, training_id,
        status="slides_generated",
        slides_url=slides_url,
        slides_presentation_id=presentation_id,
    )

    return {
        "training": updated,
        "slides_url": slides_url,
        "presentation_id": presentation_id,
    }
