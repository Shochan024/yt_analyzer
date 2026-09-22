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
            "long_tail_ratio": 0.4,
            "max_views_per_day": 500
          }
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


if __name__ == "__main__":
  unittest.main()
