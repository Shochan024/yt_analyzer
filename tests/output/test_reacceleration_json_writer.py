import json
import tempfile
import unittest
from pathlib import Path

from src.yt_analyzer.output.reacceleration_json_writer import (
  ReaccelerationJsonWriter,
)
from src.yt_analyzer.performance.result import (
  PerformanceResult,
  ReaccelerationPoint,
)


def create_record(
  video_id: str,
  points: tuple[ReaccelerationPoint, ...]
) -> PerformanceResult:
  return PerformanceResult(
    video_id=video_id,
    first_day_views=100,
    initial_peak_day=1,
    initial_peak_views=100,
    max_views_day=1,
    max_views_per_day=100,
    breakpoint_day=2,
    views_at_breakpoint=50,
    pre_break_slope=-50.0,
    post_break_slope=0.0,
    decay_ratio=0.2,
    long_tail_ratio=0.8,
    post_break_peak_day=20,
    post_break_peak_views=150,
    post_break_peak_ratio=1.5,
    cumulative_views_3d=180,
    cumulative_views_7d=220,
    cumulative_views_10d=250,
    cumulative_views_30d=None,
    cumulative_views_90d=None,
    total_views=500,
    observed_days=20,
    initial_breakpoint_day=2,
    reacceleration_points=points,
    reacceleration_count=len(points)
  )


class ReaccelerationJsonWriterTest(unittest.TestCase):
  def setUp(self):
    self.temporary_directory = tempfile.TemporaryDirectory()
    self.path = (
      Path(self.temporary_directory.name)
      / "reacceleration_points.json"
    )
    self.writer = ReaccelerationJsonWriter()

  def tearDown(self):
    self.temporary_directory.cleanup()

  def _read(self):
    return json.loads(
      self.path.read_text(
        encoding="utf-8"
      )
    )

  def test_write_serializes_multiple_points(self):
    points = (
      ReaccelerationPoint(
        day=12,
        views=20,
        slope_before=-1.0,
        slope_after=3.0,
        strength=4.0
      ),
      ReaccelerationPoint(
        day=24,
        views=40,
        slope_before=0.0,
        slope_after=6.0,
        strength=6.0
      )
    )

    self.writer.write(
      path=self.path,
      records=[
        create_record(
          "video-1",
          points
        )
      ]
    )

    rows = self._read()

    self.assertEqual(rows[0]["video_id"], "video-1")
    self.assertEqual(
      [point["day"] for point in rows[0]["reacceleration_points"]],
      [12, 24]
    )

  def test_upsert_replaces_only_target_video(self):
    self.writer.write(
      path=self.path,
      records=[
        create_record("video-1", ()),
        create_record("video-2", ())
      ]
    )

    self.writer.write(
      path=self.path,
      records=[
        create_record(
          "video-1",
          (
            ReaccelerationPoint(
              day=10,
              views=20,
              slope_before=0.0,
              slope_after=2.0,
              strength=2.0
            ),
          )
        )
      ],
      upsert=True
    )

    rows = self._read()
    by_video_id = {
      row["video_id"]: row
      for row in rows
    }

    self.assertEqual(len(rows), 2)
    self.assertEqual(
      by_video_id["video-1"]["reacceleration_points"][0]["day"],
      10
    )
    self.assertEqual(
      by_video_id["video-2"]["reacceleration_points"],
      []
    )


if __name__ == "__main__":
  unittest.main()
