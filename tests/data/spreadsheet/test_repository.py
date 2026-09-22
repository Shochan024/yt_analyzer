# tests/data/spreadsheet/test_repository.py

import unittest

from src.yt_analyzer.data.model import VideoType
from src.yt_analyzer.data.spreadsheet.repository import (
  SpreadsheetAnalysisDataRepository,
)


class FakeSpreadsheetClient:
  def __init__(self, records_by_worksheet):
    self._records_by_worksheet = records_by_worksheet

  def records(self, worksheet_name: str) -> list[dict[str, object]]:
    return self._records_by_worksheet.get(
      worksheet_name,
      []
    )


class SpreadsheetAnalysisDataRepositoryTest(unittest.TestCase):
  def test_videos_returns_video_records(self):
    client = FakeSpreadsheetClient(
      {
        "videos": [
          {
            "video_id": "video-1",
            "title": "テスト動画",
            "video_type": "long",
            "published_at": "2026-09-20T12:30:00",
            "ctr": 5.2,
            "average_percentage_viewed": 43.5,
            "stayed_to_watch": "",
            "engaged_views": 1000
          }
        ]
      }
    )

    repository = SpreadsheetAnalysisDataRepository(
      client=client
    )

    records = repository.videos()

    self.assertEqual(
      len(records),
      1
    )

    record = records[0]

    self.assertEqual(
      record.video_id,
      "video-1"
    )

    self.assertEqual(
      record.title,
      "テスト動画"
    )

    self.assertEqual(
      record.video_type,
      VideoType.LONG
    )

    self.assertEqual(
      record.published_at.year,
      2026
    )

    self.assertEqual(
      record.published_at.month,
      9
    )

    self.assertEqual(
      record.published_at.day,
      20
    )

    self.assertEqual(
      record.ctr,
      5.2
    )

    self.assertEqual(
      record.average_percentage_viewed,
      43.5
    )

    self.assertIsNone(
      record.stayed_to_watch
    )

    self.assertEqual(
      record.engaged_views,
      1000
    )

  def test_video_type_is_normalized(self):
    client = FakeSpreadsheetClient(
      {
        "videos": [
          {
            "video_id": "video-1",
            "title": "Long",
            "video_type": "LONG",
            "published_at": "2026-09-20T12:30:00",
            "ctr": "",
            "average_percentage_viewed": "",
            "stayed_to_watch": "",
            "engaged_views": ""
          },
          {
            "video_id": "video-2",
            "title": "Short",
            "video_type": "Short",
            "published_at": "2026-09-20T12:30:00",
            "ctr": "",
            "average_percentage_viewed": "",
            "stayed_to_watch": "",
            "engaged_views": ""
          }
        ]
      }
    )

    repository = SpreadsheetAnalysisDataRepository(
      client=client
    )

    records = repository.videos()

    self.assertEqual(
      records[0].video_type,
      VideoType.LONG
    )

    self.assertEqual(
      records[1].video_type,
      VideoType.SHORT
    )

  def test_percentage_string_is_converted_to_float(self):
    client = FakeSpreadsheetClient(
      {
        "videos": [
          {
            "video_id": "video-1",
            "title": "テスト動画",
            "video_type": "long",
            "published_at": "2026-09-20T12:30:00",
            "ctr": "5.2%",
            "average_percentage_viewed": "43.5%",
            "stayed_to_watch": "70.1%",
            "engaged_views": "1000"
          }
        ]
      }
    )

    repository = SpreadsheetAnalysisDataRepository(
      client=client
    )

    record = repository.videos()[0]

    self.assertEqual(
      record.ctr,
      5.2
    )

    self.assertEqual(
      record.average_percentage_viewed,
      43.5
    )

    self.assertEqual(
      record.stayed_to_watch,
      70.1
    )

  def test_blank_values_are_converted_to_none(self):
    client = FakeSpreadsheetClient(
      {
        "videos": [
          {
            "video_id": "video-1",
            "title": "テスト動画",
            "video_type": "long",
            "published_at": "2026-09-20T12:30:00",
            "ctr": "",
            "average_percentage_viewed": " ",
            "stayed_to_watch": None,
            "engaged_views": ""
          }
        ]
      }
    )

    repository = SpreadsheetAnalysisDataRepository(
      client=client
    )

    record = repository.videos()[0]

    self.assertIsNone(
      record.ctr
    )

    self.assertIsNone(
      record.average_percentage_viewed
    )

    self.assertIsNone(
      record.stayed_to_watch
    )

    self.assertIsNone(
      record.engaged_views
    )

  def test_daily_metrics_filters_by_video_id(self):
    client = FakeSpreadsheetClient(
      {
        "daily_metrics": [
          {
            "video_id": "video-1",
            "date": "2026-09-20",
            "elapsed_day": 1,
            "daily_views": 100,
            "cumulative_views": 100
          },
          {
            "video_id": "video-2",
            "date": "2026-09-20",
            "elapsed_day": 1,
            "daily_views": 500,
            "cumulative_views": 500
          },
          {
            "video_id": "video-1",
            "date": "2026-09-21",
            "elapsed_day": 2,
            "daily_views": 200,
            "cumulative_views": 300
          }
        ]
      }
    )

    repository = SpreadsheetAnalysisDataRepository(
      client=client
    )

    records = repository.daily_metrics(
      "video-1"
    )

    self.assertEqual(
      len(records),
      2
    )

    self.assertEqual(
      records[0].video_id,
      "video-1"
    )

    self.assertEqual(
      records[1].video_id,
      "video-1"
    )

  def test_daily_metrics_are_sorted_by_elapsed_day(self):
    client = FakeSpreadsheetClient(
      {
        "daily_metrics": [
          {
            "video_id": "video-1",
            "date": "2026-09-22",
            "elapsed_day": 3,
            "daily_views": 300,
            "cumulative_views": 600
          },
          {
            "video_id": "video-1",
            "date": "2026-09-20",
            "elapsed_day": 1,
            "daily_views": 100,
            "cumulative_views": 100
          },
          {
            "video_id": "video-1",
            "date": "2026-09-21",
            "elapsed_day": 2,
            "daily_views": 200,
            "cumulative_views": 300
          }
        ]
      }
    )

    repository = SpreadsheetAnalysisDataRepository(
      client=client
    )

    records = repository.daily_metrics(
      "video-1"
    )

    self.assertEqual(
      [
        record.elapsed_day
        for record in records
      ],
      [1, 2, 3]
    )

  def test_daily_metric_values_are_converted(self):
    client = FakeSpreadsheetClient(
      {
        "daily_metrics": [
          {
            "video_id": "video-1",
            "date": "2026-09-20",
            "elapsed_day": "1",
            "daily_views": "100",
            "cumulative_views": "100"
          }
        ]
      }
    )

    repository = SpreadsheetAnalysisDataRepository(
      client=client
    )

    record = repository.daily_metrics(
      "video-1"
    )[0]

    self.assertEqual(
      record.date.year,
      2026
    )

    self.assertEqual(
      record.date.month,
      9
    )

    self.assertEqual(
      record.date.day,
      20
    )

    self.assertEqual(
      record.elapsed_day,
      1
    )

    self.assertEqual(
      record.daily_views,
      100
    )

    self.assertEqual(
      record.cumulative_views,
      100
    )

  def test_unknown_video_type_raises_error(self):
    client = FakeSpreadsheetClient(
      {
        "videos": [
          {
            "video_id": "video-1",
            "title": "テスト動画",
            "video_type": "unknown",
            "published_at": "2026-09-20T12:30:00",
            "ctr": "",
            "average_percentage_viewed": "",
            "stayed_to_watch": "",
            "engaged_views": ""
          }
        ]
      }
    )

    repository = SpreadsheetAnalysisDataRepository(
      client=client
    )

    with self.assertRaises(ValueError):
      repository.videos()
