import unittest

from src.yt_analyzer.report.daily_metrics import ReportDailyMetricsLoader


class FakeSpreadsheetClient:
  def records(self, worksheet_name):
    self.worksheet_name = worksheet_name

    return [
      {
        "video_id": "video-1",
        "elapsed_day": "",
        "daily_views": 0,
        "cumulative_views": ""
      },
      {
        "video_id": "video-1",
        "elapsed_day": 2,
        "daily_views": 20,
        "cumulative_views": 30
      },
      {
        "video_id": "video-1",
        "elapsed_day": 1,
        "daily_views": 10,
        "cumulative_views": 10
      },
      {
        "video_id": "video-2",
        "elapsed_day": 1,
        "daily_views": 50,
        "cumulative_views": 50
      }
    ]


class ReportDailyMetricsLoaderTest(unittest.TestCase):
  def test_load_groups_and_sorts_published_daily_metrics(self):
    client = FakeSpreadsheetClient()
    data = ReportDailyMetricsLoader(client=client).load()

    self.assertEqual(client.worksheet_name, "daily_metrics")
    self.assertEqual(
      data["video-1"],
      [
        {
          "elapsed_day": 1,
          "daily_views": 10,
          "cumulative_views": 10
        },
        {
          "elapsed_day": 2,
          "daily_views": 20,
          "cumulative_views": 30
        }
      ]
    )
    self.assertEqual(
      data["video-2"][0]["cumulative_views"],
      50
    )


if __name__ == "__main__":
  unittest.main()
