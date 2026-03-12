"""Fetch images from Unsplash API for slides."""
import httpx
from app.config import UNSPLASH_ACCESS_KEY


async def fetch_image_url(query: str) -> str | None:
    """
    Search Unsplash for a relevant image. Returns the image URL or None if not found/configured.
    """
    if not UNSPLASH_ACCESS_KEY or not query or not query.strip():
        return None

    search = query.strip()[:100]  # Limit length
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": search,
        "per_page": 1,
        "orientation": "landscape",
        "content_filter": "high",
    }
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            if results:
                # Use 'regular' size (1080px wide) - good for slides
                return results[0].get("urls", {}).get("regular")
    except Exception:
        pass
    return None
