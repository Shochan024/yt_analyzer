import unittest
from datetime import date, datetime
from zoneinfo import ZoneInfo

from src.yt_analyzer.application.performance_metrics_runner import (
  PerformanceMetricsRunner
)
from src.yt_analyzer.data.model import DailyMetricRecord, VideoRecord, VideoType
from src.yt_analyzer.data.repository import AnalysisDataRepository
from src.yt_analyzer.performance.result import PerformanceResult


class FakeRepository(AnalysisDataRepository):
  def __init__(
    self,
    videos: list[VideoRecord],
    metrics: dict[str, list[DailyMetricRecord]]
  ) -> None:
    self._videos = videos
    self._metrics = metrics

  def videos(self) -> list[VideoRecord]:
    return self._videos

  def daily_metrics(self, video_id: str) -> list[DailyMetricRecord]:
    return self._metrics.get(video_id, [])


class FakePerformanceAnalyzer:
  def __init__(self) -> None:
    self.series = []

  def analyze(self, series):
    self.series.append(series)

    return PerformanceResult(
      video_id=series.video_id,
      first_day_views=100,
      initial_peak_day=None,
      initial_peak_views=None,
      max_views_day=2,
      max_views_per_day=200,
      breakpoint_day=None,
      views_at_breakpoint=None,
      pre_break_slope=None,
      post_break_slope=None,
      decay_ratio=None,
      long_tail_ratio=None,
      post_break_peak_day=None,
      post_break_peak_views=None,
      post_break_peak_ratio=None,
      cumulative_views_3d=None,
      cumulative_views_7d=None,
      cumulative_views_10d=None,
      cumulative_views_30d=None,
      cumulative_views_90d=None,
      total_views=300,
      observed_days=2
    )


def create_video(video_id: str, video_type: VideoType) -> VideoRecord:
  return VideoRecord(
    video_id=video_id,
    title=f"title-{video_id}",
    video_type=video_type,
    published_at=datetime(
      2026,
      9,
      20,
      12,
      0,
      tzinfo=ZoneInfo("Asia/Tokyo")
    ),
    ctr=None,
    average_percentage_viewed=None,
    stayed_to_watch=None,
    engaged_views=None
  )


def create_metric(
  video_id: str,
  elapsed_day: int,
  daily_views: int
) -> DailyMetricRecord:
  return DailyMetricRecord(
    video_id=video_id,
    date=date(2026, 9, 19 + elapsed_day),
    elapsed_day=elapsed_day,
    daily_views=daily_views,
    cumulative_views=None
  )


class PerformanceMetricsRunnerTest(unittest.TestCase):
  def setUp(self):
    self.videos = [
      create_video("video-1", VideoType.LONG),
      create_video("video-2", VideoType.SHORT)
    ]

    self.repository = FakeRepository(
      videos=self.videos,
      metrics={
        "video-1": [
          create_metric("video-1", 1, 100),
          create_metric("video-1", 2, 200)
        ],
        "video-2": [
          create_metric("video-2", 1, 300)
        ]
      }
    )

    self.analyzer = FakePerformanceAnalyzer()
    self.runner = PerformanceMetricsRunner(
      repository=self.repository,
      analyzer=self.analyzer
    )

  def test_run_returns_all_videos_when_video_id_is_not_given(self):
    records = self.runner.run()

    self.assertEqual(
      [record.video_id for record in records],
      ["video-1", "video-2"]
    )
    self.assertEqual(
      [series.video_id for series in self.analyzer.series],
      ["video-1", "video-2"]
    )

  def test_run_returns_only_specified_video(self):
    records = self.runner.run(video_id="video-2")

    self.assertEqual(len(records), 1)
    self.assertEqual(records[0].video_id, "video-2")
    self.assertEqual(len(self.analyzer.series), 1)
    self.assertEqual(self.analyzer.series[0].video_id, "video-2")

  def test_run_raises_when_video_id_does_not_exist(self):
    with self.assertRaisesRegex(
      ValueError,
      "Video not found: missing"
    ):
      self.runner.run(video_id="missing")

  def test_run_converts_daily_metrics_to_daily_view_series(self):
    self.runner.run(video_id="video-1")

    series = self.analyzer.series[0]

    self.assertEqual(series.video_id, "video-1")
    self.assertEqual(
      [(daily_view.day, daily_view.views) for daily_view in series.daily_views],
      [(1, 100), (2, 200)]
    )

  def test_run_skips_video_without_daily_metrics(self):
    repository = FakeRepository(
      videos=self.videos,
      metrics={
        "video-1": [
          create_metric("video-1", 1, 100)
        ]
      }
    )
    analyzer = FakePerformanceAnalyzer()
    runner = PerformanceMetricsRunner(
      repository=repository,
      analyzer=analyzer
    )

    records = runner.run()

    self.assertEqual(
      [record.video_id for record in records],
      ["video-1"]
    )
    self.assertEqual(
      [series.video_id for series in analyzer.series],
      ["video-1"]
    )


if __name__ == "__main__":
  unittest.main()
