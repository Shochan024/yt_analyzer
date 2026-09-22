import csv
import tempfile
import unittest
from pathlib import Path

from src.yt_analyzer.output.performance_csv_writer import PerformanceCsvWriter
from src.yt_analyzer.performance.result import PerformanceResult


def create_record(
  video_id: str,
  total_views: int
) -> PerformanceResult:
  return PerformanceResult(
    video_id=video_id,
    first_day_views=100,
    initial_peak_day=2,
    initial_peak_views=200,
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
    total_views=total_views,
    observed_days=2
  )


class PerformanceCsvWriterTest(unittest.TestCase):
  def setUp(self):
    self.writer = PerformanceCsvWriter()
    self.temporary_directory = tempfile.TemporaryDirectory()
    self.path = (
      Path(self.temporary_directory.name)
      / "nested"
      / "performance.csv"
    )

  def tearDown(self):
    self.temporary_directory.cleanup()

  def _read_rows(self) -> list[dict[str, str]]:
    with self.path.open("r", encoding="utf-8", newline="") as file:
      return list(csv.DictReader(file))

  def test_write_creates_csv_with_header_and_records(self):
    self.writer.write(
      path=self.path,
      records=[
        create_record("video-1", 300),
        create_record("video-2", 500)
      ]
    )

    rows = self._read_rows()

    self.assertEqual(len(rows), 2)
    self.assertEqual(rows[0]["video_id"], "video-1")
    self.assertEqual(rows[0]["total_views"], "300")
    self.assertEqual(
      list(rows[0].keys()),
      list(PerformanceCsvWriter.FIELD_NAMES)
    )

  def test_write_recreates_entire_csv_when_upsert_is_false(self):
    self.writer.write(
      path=self.path,
      records=[create_record("old-video", 100)]
    )

    self.writer.write(
      path=self.path,
      records=[
        create_record("video-1", 300),
        create_record("video-2", 500)
      ],
      upsert=False
    )

    rows = self._read_rows()

    self.assertEqual(
      [row["video_id"] for row in rows],
      ["video-1", "video-2"]
    )

  def test_write_replaces_existing_video_when_upsert_is_true(self):
    self.writer.write(
      path=self.path,
      records=[
        create_record("video-1", 300),
        create_record("video-2", 500)
      ]
    )

    self.writer.write(
      path=self.path,
      records=[create_record("video-1", 999)],
      upsert=True
    )

    rows = self._read_rows()
    rows_by_video_id = {
      row["video_id"]: row
      for row in rows
    }

    self.assertEqual(len(rows), 2)
    self.assertEqual(rows_by_video_id["video-1"]["total_views"], "999")
    self.assertEqual(rows_by_video_id["video-2"]["total_views"], "500")

  def test_write_adds_new_video_when_upsert_is_true(self):
    self.writer.write(
      path=self.path,
      records=[create_record("video-1", 300)]
    )

    self.writer.write(
      path=self.path,
      records=[create_record("video-2", 500)],
      upsert=True
    )

    rows = self._read_rows()

    self.assertEqual(
      [row["video_id"] for row in rows],
      ["video-1", "video-2"]
    )


if __name__ == "__main__":
  unittest.main()
