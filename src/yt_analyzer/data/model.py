# src/yt_analyzer/data/model.py

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class VideoType(Enum):
  LONG = "long"
  SHORT = "short"


@dataclass(frozen=True)
class VideoRecord:
  video_id: str
  title: str
  video_type: VideoType
  published_at: datetime

  ctr: float | None
  average_percentage_viewed: float | None
  stayed_to_watch: float | None
  engaged_views: int | None


@dataclass(frozen=True)
class DailyMetricRecord:
  video_id: str
  date: date
  elapsed_day: int
  daily_views: int
  cumulative_views: int | None
