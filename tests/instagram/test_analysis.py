import unittest

from src.yt_analyzer.application.instagram_features_runner import (
  InstagramFeatureRecord,
)
from src.yt_analyzer.instagram.analysis import InstagramAnalyzer


def record(
  post_id: str,
  length: int,
  reach: int,
  post_type: str = "image"
) -> InstagramFeatureRecord:
  return InstagramFeatureRecord(
    post_id=post_id,
    caption=f"caption {post_id}",
    post_type=post_type,
    published_at="2026-09-22T12:00:00",
    link=None,
    duration_seconds=None,
    length=length,
    word_count=length,
    mean_contextual_surprisal=float(length),
    proper_noun_ratio=0.1 * length,
    number_count=length,
    unigram_cross_entropy=float(length),
    views=reach * 2,
    reach=reach,
    likes=reach // 10,
    shares=1,
    follows=1,
    comments=1,
    saves=1,
    like_rate=0.1,
    share_rate=0.01,
    follow_rate=0.01,
    comment_rate=0.01,
    save_rate=0.01,
    engagement_rate=0.13
  )


class InstagramAnalyzerTest(unittest.TestCase):
  def test_analyzes_each_post_type_independently(self):
    results = InstagramAnalyzer().analyze([
      record("1", 1, 100, "image"),
      record("2", 2, 200, "image"),
      record("3", 3, 300, "image"),
      record("4", 1, 50, "reel")
    ])

    image = results["image"]
    reel = results["reel"]

    self.assertEqual(image.sample_size, 3)
    self.assertEqual(reel.sample_size, 1)
    self.assertAlmostEqual(
      image.correlations["reach"]["length"].pearson,
      1.0
    )
    self.assertAlmostEqual(
      image.regressions["reach"]["length"].coefficient,
      100.0
    )
    self.assertIsNone(
      reel.correlations["reach"]["length"].pearson
    )


if __name__ == "__main__":
  unittest.main()
