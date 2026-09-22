import tempfile
import unittest
from pathlib import Path

from src.yt_analyzer.report.renderer import ChannelReportRenderer


class ChannelReportRendererTest(unittest.TestCase):
  def test_write_creates_self_contained_html(self):
    data = {
      "videos": [
        {
          "video_id": "video-1",
          "title": "Test </script> Video",
          "video_type": "long",
          "features": {
            "length": 20
          },
          "metrics": {
            "ctr": 0.05
          },
          "performance": {
            "cumulative_views_7d": 1000,
            "breakpoint_day": 3,
            "initial_breakpoint_day": 3,
            "reacceleration_count": 1,
            "primary_reacceleration_day": 5,
            "post_break_peak_day": 7,
            "long_tail_ratio": 0.4,
            "max_views_per_day": 500
          },
          "reacceleration_points": [
            {
              "day": 5,
              "views": 300,
              "slope_before": -1.0,
              "slope_after": 4.0,
              "strength": 5.0
            }
          ],
          "daily_metrics": [
            {
              "elapsed_day": 1,
              "daily_views": 100,
              "cumulative_views": 100
            },
            {
              "elapsed_day": 3,
              "daily_views": 200,
              "cumulative_views": 500
            },
            {
              "elapsed_day": 5,
              "daily_views": 300,
              "cumulative_views": 800
            },
            {
              "elapsed_day": 7,
              "daily_views": 500,
              "cumulative_views": 1300
            }
          ]
        }
      ],
      "analysis": {
        "long": {
          "correlations": {},
          "regressions": {}
        },
        "short": {
          "correlations": {},
          "regressions": {}
        }
      },
      "kpis": {
        "long": {
          "video_count": 1
        },
        "short": {
          "video_count": 0
        }
      }
    }

    with tempfile.TemporaryDirectory() as directory:
      path = Path(directory) / "channel_report.html"
      ChannelReportRenderer().write(
        path=path,
        data=data
      )
      html = path.read_text(encoding="utf-8")

    self.assertIn("<!doctype html>", html)
    self.assertIn("window.REPORT_DATA", html)
    self.assertIn("Test <\\/script> Video", html)
    self.assertIn('data-mode="long"', html)
    self.assertIn('id="scatter"', html)
    self.assertIn("mouseenter", html)
    self.assertIn("click", html)
    self.assertIn("regression-line", html)
    self.assertIn("bar-zero", html)
    self.assertIn('direction = numericValue !== null && numericValue < 0', html)
    self.assertIn('id="feature-table"', html)
    self.assertIn('data-feature-sort="mean_contextual_surprisal"', html)
    self.assertIn("renderFeatureTable", html)
    self.assertIn('id="cumulative-chart"', html)
    self.assertIn("breakpoint-line", html)
    self.assertIn("cumulative-point", html)
    self.assertIn("renderCumulativeChart", html)
    self.assertIn("reacceleration-line", html)
    self.assertIn("post-break-peak-marker", html)
    self.assertIn("primary_reacceleration_day", html)
    self.assertIn("初動終了", html)
    self.assertIn("再加速", html)


if __name__ == "__main__":
  unittest.main()
