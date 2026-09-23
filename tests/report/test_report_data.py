import json
import tempfile
import unittest
from pathlib import Path

from src.yt_analyzer.report.data import ReportDataBuilder


class ReportDataBuilderTest(unittest.TestCase):
  def test_build_joins_video_data_and_calculates_kpis(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      title_path = root / "title_features.csv"
      performance_path = root / "performance.csv"
      long_path = root / "long_analysis.json"
      short_path = root / "short_analysis.json"
      reacceleration_path = root / "reacceleration_points.json"
      title_feature_details_path = root / "title_feature_details.json"

      title_path.write_text(
        "video_id,title,video_type,length,word_count,"
        "mean_contextual_surprisal,proper_noun_ratio,number_count,"
        "unigram_cross_entropy,ctr,average_percentage_viewed,"
        "stayed_to_watch,engaged_views,likes,subscribers_gained,"
        "comments,published_at\n"
        "long-1,Long 1,long,20,8,4.5,0.2,1,9.0,0.04,0.37,,,28,7,1,2026-06-22\n"
        "long-2,Long 2,long,24,10,4.8,0.1,0,9.4,0.06,0.29,,,14,4,2,2026-08-21\n"
        "short-1,Short 1,short,18,7,5.0,0.3,1,10.0,0.07,0.55,0.65,120,13,0,1,2026-09-19\n",
        encoding="utf-8"
      )

      performance_path.write_text(
        "video_id,first_day_views,initial_peak_day,initial_peak_views,"
        "max_views_day,max_views_per_day,breakpoint_day,views_at_breakpoint,"
        "pre_break_slope,post_break_slope,decay_ratio,long_tail_ratio,"
        "post_break_peak_day,post_break_peak_views,post_break_peak_ratio,"
        "cumulative_views_3d,cumulative_views_7d,cumulative_views_10d,"
        "cumulative_views_30d,cumulative_views_90d,total_views,observed_days\n"
        "long-1,100,1,100,2,200,3,300,1.0,0.2,0.2,0.4,5,80,0.8,"
        "300,700,900,1200,1500,1600,100\n"
        "short-1,300,1,300,1,300,2,500,1.0,0.3,0.3,0.2,3,100,0.3,"
        "700,1000,1200,1400,1500,1600,20\n",
        encoding="utf-8"
      )

      long_path.write_text(
        json.dumps({"correlations": {}, "regressions": {}, "sample_size": 2}),
        encoding="utf-8"
      )
      short_path.write_text(
        json.dumps({"correlations": {}, "regressions": {}, "sample_size": 1}),
        encoding="utf-8"
      )
      title_feature_details_path.write_text(
        json.dumps(
          [
            {
              "video_id": "long-1",
              "proper_nouns": ["神戸", "有馬温泉"],
              "unigram_top_words": [
                {
                  "text": "じもみん",
                  "score": 12.3
                }
              ],
              "contextual_top_tokens": [
                {
                  "text": "不可避",
                  "score": 9.4
                }
              ]
            }
          ]
        ),
        encoding="utf-8"
      )
      reacceleration_path.write_text(
        json.dumps(
          [
            {
              "video_id": "long-1",
              "reacceleration_points": [
                {
                  "start_day": 11,
                  "start_views": 16,
                  "peak_strength_day": 12,
                  "peak_strength_views": 20,
                  "slope_before": -1.0,
                  "slope_after": 3.0,
                  "strength": 4.0
                }
              ]
            }
          ]
        ),
        encoding="utf-8"
      )

      data = ReportDataBuilder().build(
        title_features_path=title_path,
        performance_path=performance_path,
        long_analysis_path=long_path,
        short_analysis_path=short_path,
        reacceleration_path=reacceleration_path,
        title_feature_details_path=title_feature_details_path,
        daily_metrics={
          "long-1": [
            {
              "elapsed_day": 1,
              "daily_views": 100,
              "cumulative_views": 100
            },
            {
              "elapsed_day": 2,
              "daily_views": 200,
              "cumulative_views": 300
            }
          ]
        }
      )

    self.assertEqual(len(data["videos"]), 3)
    self.assertEqual(data["videos"][0]["performance"]["cumulative_views_7d"], 700)
    self.assertEqual(
      data["videos"][0]["daily_metrics"][1]["cumulative_views"],
      300
    )
    self.assertEqual(
      data["videos"][0]["reacceleration_points"][0]["start_day"],
      11
    )
    self.assertEqual(
      data["videos"][0]["reacceleration_points"][0]["peak_strength_day"],
      12
    )
    self.assertEqual(
      data["videos"][0]["feature_details"]["proper_nouns"],
      ["神戸", "有馬温泉"]
    )
    self.assertEqual(
      data["videos"][0]["feature_details"]["unigram_top_words"][0]["text"],
      "じもみん"
    )
    self.assertEqual(
      data["videos"][0]["feature_details"]["contextual_top_tokens"][0]["text"],
      "不可避"
    )
    self.assertIsNone(
      data["videos"][1]["performance"]["cumulative_views_7d"]
    )
    self.assertEqual(
      data["videos"][0]["metrics"]["likes"],
      28
    )
    self.assertEqual(
      data["videos"][0]["metrics"]["subscribers_gained"],
      7
    )
    self.assertEqual(
      data["videos"][0]["metrics"]["comments"],
      1
    )
    self.assertEqual(data["kpis"]["long"]["video_count"], 2)
    self.assertAlmostEqual(data["kpis"]["long"]["average_ctr"], 0.05)
    self.assertEqual(
      data["kpis"]["long"]["average_cumulative_views_7d"],
      700
    )
    self.assertAlmostEqual(
      data["kpis"]["short"]["average_stayed_to_watch"],
      0.65
    )

  def test_build_raises_when_input_is_missing(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)

      with self.assertRaisesRegex(
        FileNotFoundError,
        "Report input not found"
      ):
        ReportDataBuilder().build(
          title_features_path=root / "missing.csv",
          performance_path=root / "performance.csv",
          long_analysis_path=root / "long.json",
          short_analysis_path=root / "short.json"
        )


if __name__ == "__main__":
  unittest.main()
