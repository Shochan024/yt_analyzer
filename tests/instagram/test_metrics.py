import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from src.yt_analyzer.instagram.metrics import InstagramMetricsCalculator
from src.yt_analyzer.instagram.model import InstagramPostRecord, InstagramPostType


class InstagramMetricsCalculatorTest(unittest.TestCase):
  def test_calculates_reach_based_rates(self):
    post = InstagramPostRecord(
      post_id="1",
      caption="caption",
      post_type=InstagramPostType.REEL,
      published_at=datetime(
        2026,
        9,
        22,
        23,
        48,
        tzinfo=ZoneInfo("Asia/Tokyo")
      ),
      link=None,
      duration_seconds=38,
      views=1000,
      reach=100,
      likes=10,
      shares=3,
      follows=2,
      comments=4,
      saves=5
    )

    result = InstagramMetricsCalculator().calculate(post)

    self.assertAlmostEqual(result.like_rate, 0.10)
    self.assertAlmostEqual(result.share_rate, 0.03)
    self.assertAlmostEqual(result.follow_rate, 0.02)
    self.assertAlmostEqual(result.comment_rate, 0.04)
    self.assertAlmostEqual(result.save_rate, 0.05)
    self.assertAlmostEqual(result.engagement_rate, 0.22)

  def test_returns_none_rates_when_reach_is_zero(self):
    post = InstagramPostRecord(
      post_id="1",
      caption="caption",
      post_type=InstagramPostType.IMAGE,
      published_at=datetime(
        2026,
        9,
        22,
        23,
        48,
        tzinfo=ZoneInfo("Asia/Tokyo")
      ),
      link=None,
      duration_seconds=None,
      views=0,
      reach=0,
      likes=1,
      shares=1,
      follows=1,
      comments=1,
      saves=1
    )

    result = InstagramMetricsCalculator().calculate(post)

    self.assertIsNone(result.like_rate)
    self.assertIsNone(result.engagement_rate)


if __name__ == "__main__":
  unittest.main()
