from ..data.model import VideoRecord
from ..data.repository import AnalysisDataRepository
from ..performance.analyzer import PerformanceAnalyzer
from ..performance.dataset import DailyView, DailyViewSeries
from ..performance.result import PerformanceResult


class PerformanceMetricsRunner:
  def __init__(
    self,
    repository: AnalysisDataRepository,
    analyzer: PerformanceAnalyzer
  ) -> None:
    self._repository = repository
    self._analyzer = analyzer

  def run(self, video_id: str | None = None) -> list[PerformanceResult]:
    videos = self._repository.videos()
    targets = self._targets(videos, video_id)

    return [
      self._analyze(video)
      for video in targets
    ]

  def _targets(
    self,
    videos: list[VideoRecord],
    video_id: str | None
  ) -> list[VideoRecord]:
    if video_id is None:
      return videos

    targets = [
      video
      for video in videos
      if video.video_id == video_id
    ]

    if not targets:
      raise ValueError(f"Video not found: {video_id}")

    return targets

  def _analyze(self, video: VideoRecord) -> PerformanceResult:
    metrics = self._repository.daily_metrics(video.video_id)

    series = DailyViewSeries(
      video_id=video.video_id,
      daily_views=[
        DailyView(
          day=metric.elapsed_day,
          views=metric.daily_views
        )
        for metric in metrics
      ]
    )

    return self._analyzer.analyze(series)
