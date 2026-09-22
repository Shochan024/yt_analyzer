# src/yt_analyzer/performance/dataset.py

from dataclasses import dataclass


@dataclass(frozen=True)
class DailyView:
  day: int
  views: int


@dataclass(frozen=True)
class DailyViewSeries:
  video_id: str
  daily_views: list[DailyView]
