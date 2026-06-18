"""
backend/tools/youtube_search.py
--------------------------------
YouTube video recommendations using youtube-search-python (no API key).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from youtubesearchpython import VideosSearch
from backend.core.config import settings
from backend.utils.logger import logger


@dataclass
class VideoResult:
    title: str
    channel: str
    url: str
    thumbnail: str
    duration: str
    views: str


def search_youtube(topic: str, max_results: int | None = None) -> List[VideoResult]:
    """Search YouTube for educational videos about `topic`."""
    n = max_results or settings.max_youtube_results
    query = f"{topic} explained tutorial"
    logger.info(f"YouTube search: {query!r} (max={n})")

    try:
        search = VideosSearch(query, limit=n)
        items = search.result().get("result", [])
    except Exception as exc:
        logger.error(f"YouTube search failed: {exc}")
        return []

    videos: List[VideoResult] = []
    for item in items:
        try:
            thumbnails = item.get("thumbnails", [{}])
            videos.append(VideoResult(
                title=item.get("title", "Unknown"),
                channel=item.get("channel", {}).get("name", "Unknown"),
                url=item.get("link", ""),
                thumbnail=thumbnails[0].get("url", "") if thumbnails else "",
                duration=item.get("duration", "N/A"),
                views=item.get("viewCount", {}).get("short", "N/A"),
            ))
        except Exception as exc:
            logger.debug(f"Skipping malformed video: {exc}")

    logger.info(f"Found {len(videos)} YouTube videos.")
    return videos
