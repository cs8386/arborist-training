"""Google Slides API service - creates presentations matching app theme."""
import uuid
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# App theme colors (from style.css) - RGB 0-1 for Slides API
THEME = {
    "bg": {"red": 13/255, "green": 17/255, "blue": 23/255},      # #0d1117
    "bg_elevated": {"red": 22/255, "green": 27/255, "blue": 34/255},  # #161b22
    "text": {"red": 230/255, "green": 237/255, "blue": 243/255},  # #e6edf3
    "text_muted": {"red": 139/255, "green": 148/255, "blue": 158/255},  # #8b949e
    "accent": {"red": 63/255, "green": 185/255, "blue": 80/255},   # #3fb950
}


def _rgb(red: float, green: float, blue: float) -> dict:
    return {"opaqueColor": {"rgbColor": {"red": red, "green": green, "blue": blue}}}


def get_slides_service(credentials_dict: dict):
    """Build Google Slides API service from OAuth credentials."""
    creds = Credentials(
        token=credentials_dict.get("token"),
        refresh_token=credentials_dict.get("refresh_token"),
        token_uri=credentials_dict.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=credentials_dict.get("client_id"),
        client_secret=credentials_dict.get("client_secret"),
        scopes=credentials_dict.get("scopes", []),
    )
    return build("slides", "v1", credentials=creds)


def get_drive_service(credentials_dict: dict):
    """Build Google Drive API service from OAuth credentials."""
    creds = Credentials(
        token=credentials_dict.get("token"),
        refresh_token=credentials_dict.get("refresh_token"),
        token_uri=credentials_dict.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=credentials_dict.get("client_id"),
        client_secret=credentials_dict.get("client_secret"),
        scopes=credentials_dict.get("scopes", []),
    )
    return build("drive", "v3", credentials=creds)


def create_presentation(credentials: dict, title: str, slides_content: list[dict]) -> tuple[str, str]:
    """
    Create a Google Slides presentation with content and save to user's Drive.

    Args:
        credentials: OAuth credentials dict from Google
        title: Presentation title
        slides_content: List of {"title": str, "content": list[str]}

    Returns:
        (presentation_id, slides_url)
    """
    service = get_slides_service(credentials)

    # Create blank presentation
    body = {"title": title}
    presentation = service.presentations().create(body=body).execute()
    presentation_id = presentation.get("presentationId")

    if not slides_content:
        return presentation_id, f"https://docs.google.com/presentation/d/{presentation_id}/edit"

    # Get the default first slide and delete it - we'll create all slides with our content
    slides = presentation.get("slides", [])
    first_slide_id = slides[0]["objectId"] if slides else None
    requests = []

    # Delete default first slide, then create all slides with our content
    if first_slide_id:
        requests.append({"deleteObject": {"objectId": first_slide_id}})

    for i, slide_data in enumerate(slides_content):
        slide_id = f"slide_{uuid.uuid4().hex[:8]}"
        title_box_id = f"title_{uuid.uuid4().hex[:8]}"
        body_box_id = f"body_{uuid.uuid4().hex[:8]}"

        requests.append({
            "createSlide": {
                "objectId": slide_id,
                "insertionIndex": str(i),
                "slideLayoutReference": {"predefinedLayout": "TITLE_AND_BODY"},
                "placeholderIdMappings": [
                    {"objectId": title_box_id, "layoutPlaceholder": {"type": "TITLE"}},
                    {"objectId": body_box_id, "layoutPlaceholder": {"type": "BODY"}},
                ],
            }
        })
        requests.append({
            "insertText": {
                "objectId": title_box_id,
                "text": slide_data["title"],
                "insertionIndex": 0,
            }
        })
        body_text = "\n".join(f"• {point}" for point in slide_data.get("content", []))
        if body_text:
            requests.append({
                "insertText": {
                    "objectId": body_box_id,
                    "text": body_text,
                    "insertionIndex": 0,
                }
            })

        # Style slides to match app theme
        requests.append({
            "updatePageProperties": {
                "objectId": slide_id,
                "pageProperties": {
                    "pageBackgroundFill": {
                        "solidFill": {"color": {"rgbColor": THEME["bg"]}}
                    }
                },
                "fields": "pageBackgroundFill.solidFill.color",
            }
        })
        requests.append({
            "updateTextStyle": {
                "objectId": title_box_id,
                "textRange": {"type": "ALL"},
                "style": {
                    "foregroundColor": _rgb(**THEME["accent"]),
                    "fontSize": {"magnitude": 28, "unit": "PT"},
                    "bold": True,
                },
                "fields": "foregroundColor,fontSize,bold",
            }
        })
        requests.append({
            "updateTextStyle": {
                "objectId": body_box_id,
                "textRange": {"type": "ALL"},
                "style": {
                    "foregroundColor": _rgb(**THEME["text"]),
                    "fontSize": {"magnitude": 14, "unit": "PT"},
                },
                "fields": "foregroundColor,fontSize",
            }
        })

    # Execute batch update
    if requests:
        body = {"requests": requests}
        service.presentations().batchUpdate(
            presentationId=presentation_id,
            body=body,
        ).execute()

    slides_url = f"https://docs.google.com/presentation/d/{presentation_id}/edit"
    return presentation_id, slides_url


