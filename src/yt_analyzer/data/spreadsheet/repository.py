# src/yt_analyzer/data/spreadsheet/repository.py

from datetime import date, datetime
from zoneinfo import ZoneInfo

from ..model import DailyMetricRecord, VideoRecord, VideoType
from ..repository import AnalysisDataRepository
from .client import SpreadsheetClient


class SpreadsheetAnalysisDataRepository(AnalysisDataRepository):
  VIDEOS_WORKSHEET = "videos"
  DAILY_METRICS_WORKSHEET = "daily_metrics"

  def __init__(self, client: SpreadsheetClient) -> None:
    self._client = client

  def videos(self) -> list[VideoRecord]:
    records = self._client.records(
      self.VIDEOS_WORKSHEET
    )

    return [
      self._video_record(
        record
      )
      for record in records
    ]

  def daily_metrics(self, video_id: str) -> list[DailyMetricRecord]:
    records = self._client.records(self.DAILY_METRICS_WORKSHEET)

    metrics = [
      self._daily_metric_record(
        record
      )
      for record in records
      if str(
        record.get("video_id", "")
      ) == video_id
    ]

    return sorted(
      metrics,
      key=lambda metric: metric.elapsed_day
    )

  def _video_record(self, record: dict[str, object]) -> VideoRecord:
    return VideoRecord(
      video_id=str(
        record["video_id"]
      ),
      title=str(
        record["title"]
      ),
      video_type=self._video_type(
        record["video_type"]
      ),
      published_at=self._datetime(
        record["published_at"]
      ),
      ctr=self._optional_float(
        record.get("ctr")
      ),
      average_percentage_viewed=self._optional_float(
        record.get("average_percentage_viewed")
      ),
      stayed_to_watch=self._optional_float(
        record.get("stayed_to_watch")
      ),
      engaged_views=self._optional_int(
        record.get("engaged_views")
      )
    )

  def _daily_metric_record(self, record: dict[str, object]) -> DailyMetricRecord:
    return DailyMetricRecord(
      video_id=str(
        record["video_id"]
      ),
      date=self._date(
        record["date"]
      ),
      elapsed_day=int(
        record["elapsed_day"]
      ),
      daily_views=int(
        record["daily_views"]
      ),
      cumulative_views=self._optional_int(
        record.get("cumulative_views")
      )
    )

  def _video_type(self, value: object) -> VideoType:
    normalized = str(
      value
    ).strip().lower()

    if normalized == VideoType.LONG.value:
      return VideoType.LONG

    if normalized == VideoType.SHORT.value:
      return VideoType.SHORT

    raise ValueError(
      f"Unknown video type: {value}"
    )

  def _datetime(self, value: object) -> datetime:
    if isinstance(value, datetime):
      if value.tzinfo is None:
        return value.replace(
          tzinfo=ZoneInfo("Asia/Tokyo")
        )

      return value

    normalized = str(value).strip()

    formats = (
      "%Y-%m-%dT%H:%M:%S",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d",
      "%Y/%m/%d %H:%M:%S",
      "%Y/%m/%d"
    )

    for date_format in formats:
      try:
        return datetime.strptime(
          normalized,
          date_format
        ).replace(
          tzinfo=ZoneInfo("Asia/Tokyo")
        )
      except ValueError:
        continue

    raise ValueError(
      f"Unsupported datetime format: {value}"
    )

  def _date(self, value: object) -> date:
    if isinstance(
      value,
      date
    ):
      return value

    return date.fromisoformat(
      str(value).strip()
    )

  def _optional_float(self, value: object) -> float | None:
    if self._blank(
      value
    ):
      return None

    if isinstance(
      value,
      str
    ):
      normalized = value.strip()

      if normalized.endswith("%"):
        return float(
          normalized[:-1]
        )

    return float(
      value
    )

  def _optional_int(self, value: object) -> int | None:
    if self._blank(
      value
    ):
      return None

    return int(
      value
    )

  def _blank(self, value: object) -> bool:
    return (
      value is None
      or (
        isinstance(value, str)
        and not value.strip()
      )
    )
