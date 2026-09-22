# src/yt_analyzer/data/repository.py

from abc import ABC, abstractmethod

from .model import DailyMetricRecord, VideoRecord


class AnalysisDataRepository(ABC):
  @abstractmethod
  def videos(self) -> list[VideoRecord]:
    raise NotImplementedError

  @abstractmethod
  def daily_metrics(self, video_id: str) -> list[DailyMetricRecord]:
    raise NotImplementedError
