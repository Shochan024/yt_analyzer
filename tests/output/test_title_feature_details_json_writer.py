import json
import tempfile
import unittest
from pathlib import Path

from src.yt_analyzer.application.title_features_runner import TitleFeatureRecord
from src.yt_analyzer.output.title_feature_details_json_writer import (
  TitleFeatureDetailsJsonWriter,
)
from src.yt_analyzer.title.features import ScoredText


def create_record(
  video_id: str,
  proper_nouns: tuple[str, ...]
) -> TitleFeatureRecord:
  return TitleFeatureRecord(
    video_id=video_id,
    title=f"title-{video_id}",
    video_type="long",
    length=10,
    word_count=4,
    mean_contextual_surprisal=5.1,
    proper_noun_ratio=0.25,
    number_count=1,
    unigram_cross_entropy=8.2,
    ctr=0.05,
    average_percentage_viewed=None,
    stayed_to_watch=None,
    engaged_views=None,
    proper_nouns=proper_nouns,
    unigram_top_words=(
      ScoredText(
        text="珍語",
        score=12.3
      ),
    ),
    contextual_top_tokens=(
      ScoredText(
        text="意外",
        score=9.4
      ),
    )
  )


class TitleFeatureDetailsJsonWriterTest(unittest.TestCase):
  def setUp(self):
    self.temporary_directory = tempfile.TemporaryDirectory()
    self.path = (
      Path(self.temporary_directory.name)
      / "title_feature_details.json"
    )
    self.writer = TitleFeatureDetailsJsonWriter()

  def tearDown(self):
    self.temporary_directory.cleanup()

  def _read(self):
    return json.loads(
      self.path.read_text(
        encoding="utf-8"
      )
    )

  def test_write_serializes_feature_details(self):
    self.writer.write(
      path=self.path,
      records=[
        create_record(
          "video-1",
          ("神戸", "有馬温泉")
        )
      ]
    )

    rows = self._read()

    self.assertEqual(
      rows[0]["proper_nouns"],
      ["神戸", "有馬温泉"]
    )
    self.assertEqual(
      rows[0]["unigram_top_words"][0]["text"],
      "珍語"
    )
    self.assertEqual(
      rows[0]["contextual_top_tokens"][0]["score"],
      9.4
    )

  def test_upsert_replaces_only_target_video(self):
    self.writer.write(
      path=self.path,
      records=[
        create_record("video-1", ("神戸",)),
        create_record("video-2", ("大阪",))
      ]
    )

    self.writer.write(
      path=self.path,
      records=[
        create_record(
          "video-1",
          ("有馬温泉",)
        )
      ],
      upsert=True
    )

    rows = self._read()
    by_video_id = {
      row["video_id"]: row
      for row in rows
    }

    self.assertEqual(len(rows), 2)
    self.assertEqual(
      by_video_id["video-1"]["proper_nouns"],
      ["有馬温泉"]
    )
    self.assertEqual(
      by_video_id["video-2"]["proper_nouns"],
      ["大阪"]
    )


if __name__ == "__main__":
  unittest.main()
