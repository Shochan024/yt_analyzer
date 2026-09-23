import unittest
from datetime import datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo

from src.yt_analyzer.application.title_features_runner import TitleFeaturesRunner
from src.yt_analyzer.data.model import DailyMetricRecord, VideoRecord, VideoType
from src.yt_analyzer.data.repository import AnalysisDataRepository
from src.yt_analyzer.title.features import ScoredText


class FakeRepository(AnalysisDataRepository):
  def __init__(self, videos: list[VideoRecord]) -> None:
    self._videos = videos

  def videos(self) -> list[VideoRecord]:
    return self._videos

  def daily_metrics(self, video_id: str) -> list[DailyMetricRecord]:
    return []


class FakeTitleAnalyzer:
  def __init__(self) -> None:
    self.analyzed_titles: list[str] = []

  def analyze(self, title: str):
    self.analyzed_titles.append(title)

    return SimpleNamespace(
      length=len(title),
      word_count=4,
      mean_contextual_surprisal=5.1,
      proper_noun_ratio=0.25,
      number_count=1,
      unigram_cross_entropy=8.2,
      proper_nouns=("神戸",),
      unigram_top_words=(
        ScoredText(text="神戸", score=8.2),
      ),
      contextual_top_tokens=(
        ScoredText(text="ある", score=6.3),
      )
    )


def create_video(
  video_id: str,
  title: str,
  video_type: VideoType
) -> VideoRecord:
  return VideoRecord(
    video_id=video_id,
    title=title,
    video_type=video_type,
    published_at=datetime(
      2026,
      9,
      20,
      12,
      0,
      tzinfo=ZoneInfo("Asia/Tokyo")
    ),
    ctr=5.2 if video_type == VideoType.LONG else None,
    average_percentage_viewed=82.0,
    stayed_to_watch=70.0 if video_type == VideoType.SHORT else None,
    engaged_views=1200 if video_type == VideoType.SHORT else None
  )


class TitleFeaturesRunnerTest(unittest.TestCase):
  def setUp(self):
    self.videos = [
      create_video(
        video_id="video-1",
        title="神戸の観光地10選",
        video_type=VideoType.LONG
      ),
      create_video(
        video_id="video-2",
        title="神戸あるある",
        video_type=VideoType.SHORT
      )
    ]
    self.repository = FakeRepository(self.videos)
    self.analyzer = FakeTitleAnalyzer()
    self.runner = TitleFeaturesRunner(
      repository=self.repository,
      analyzer=self.analyzer
    )

  def test_run_returns_all_videos_when_video_id_is_not_given(self):
    records = self.runner.run()

    self.assertEqual(
      [record.video_id for record in records],
      ["video-1", "video-2"]
    )
    self.assertEqual(
      self.analyzer.analyzed_titles,
      ["神戸の観光地10選", "神戸あるある"]
    )

  def test_run_returns_only_specified_video(self):
    records = self.runner.run(
      video_id="video-2"
    )

    self.assertEqual(
      len(records),
      1
    )
    self.assertEqual(
      records[0].video_id,
      "video-2"
    )
    self.assertEqual(
      self.analyzer.analyzed_titles,
      ["神戸あるある"]
    )

  def test_run_raises_when_video_id_does_not_exist(self):
    with self.assertRaisesRegex(
      ValueError,
      "Video not found: missing"
    ):
      self.runner.run(
        video_id="missing"
      )

  def test_run_converts_video_and_features_to_record(self):
    record = self.runner.run(
      video_id="video-2"
    )[0]

    self.assertEqual(
      record.video_id,
      "video-2"
    )
    self.assertEqual(
      record.title,
      "神戸あるある"
    )
    self.assertEqual(
      record.video_type,
      "short"
    )
    self.assertEqual(
      record.length,
      len("神戸あるある")
    )
    self.assertEqual(
      record.word_count,
      4
    )
    self.assertEqual(
      record.mean_contextual_surprisal,
      5.1
    )
    self.assertEqual(
      record.proper_noun_ratio,
      0.25
    )
    self.assertEqual(
      record.number_count,
      1
    )
    self.assertEqual(
      record.unigram_cross_entropy,
      8.2
    )
    self.assertEqual(
      record.average_percentage_viewed,
      82.0
    )
    self.assertEqual(
      record.stayed_to_watch,
      70.0
    )
    self.assertEqual(
      record.engaged_views,
      1200
    )
    self.assertEqual(
      record.proper_nouns,
      ("神戸",)
    )
    self.assertEqual(
      record.unigram_top_words[0].text,
      "神戸"
    )
    self.assertEqual(
      record.contextual_top_tokens[0].text,
      "ある"
    )


if __name__ == "__main__":
  unittest.main()
