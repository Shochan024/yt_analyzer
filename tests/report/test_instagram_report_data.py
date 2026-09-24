import math
import unittest

from src.yt_analyzer.application.instagram_features_runner import (
  InstagramFeatureRecord,
)
from src.yt_analyzer.instagram.analysis import InstagramAnalyzer
from src.yt_analyzer.report.instagram_data import InstagramReportDataBuilder


def record(
  post_id: str,
  reach: int,
  engagement_rate: float,
  follow_rate: float
) -> InstagramFeatureRecord:
  return InstagramFeatureRecord(
    post_id=post_id,
    caption=f"caption {post_id}",
    post_type="image",
    published_at="2026-09-22T12:00:00",
    link=None,
    duration_seconds=None,
    length=10,
    word_count=4,
    mean_contextual_surprisal=1.2,
    proper_noun_ratio=0.25,
    number_count=0,
    unigram_cross_entropy=2.0,
    views=reach,
    reach=reach,
    likes=10,
    shares=1,
    follows=1,
    comments=1,
    saves=1,
    like_rate=0.1,
    share_rate=0.01,
    follow_rate=follow_rate,
    comment_rate=0.01,
    save_rate=0.01,
    engagement_rate=engagement_rate
  )


class InstagramReportDataBuilderTest(unittest.TestCase):
  def test_builds_median_kpis(self):
    records = [
      record("1", 100, 0.10, 0.01),
      record("2", 300, 0.30, 0.03),
      record("3", 200, 0.20, 0.02)
    ]
    analysis = InstagramAnalyzer().analyze(records)

    data = InstagramReportDataBuilder().build(
      records=records,
      analysis=analysis
    )

    kpis = data["kpis"]["image"]

    self.assertEqual(kpis["post_count"], 3)
    self.assertEqual(kpis["median_reach"], 200.0)
    self.assertAlmostEqual(kpis["median_engagement_rate"], 0.20)
    self.assertAlmostEqual(kpis["median_follow_rate"], 0.02)

  def test_adds_log1p_metrics_for_report_visualization(self):
    records = [
      record("1", 99, 0.10, 0.01)
    ]
    analysis = InstagramAnalyzer().analyze(records)

    data = InstagramReportDataBuilder().build(
      records=records,
      analysis=analysis
    )

    metrics = data["posts"][0]["metrics"]

    self.assertAlmostEqual(
      metrics["log1p_reach"],
      math.log(100)
    )
    self.assertAlmostEqual(
      metrics["log1p_views"],
      math.log(100)
    )


if __name__ == "__main__":
  unittest.main()
