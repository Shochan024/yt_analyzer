from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class InstagramPostType(Enum):
  IMAGE = "image"
  CAROUSEL = "carousel"
  REEL = "reel"


@dataclass(frozen=True)
class InstagramPostRecord:
  post_id: str
  caption: str
  post_type: InstagramPostType
  published_at: datetime
  link: str | None
  duration_seconds: int | None

  views: int | None
  reach: int | None
  likes: int | None
  shares: int | None
  follows: int | None
  comments: int | None
  saves: int | None
