import csv
import tempfile
import unittest
from pathlib import Path

from src.yt_analyzer.application.title_features_runner import TitleFeatureRecord
from src.yt_analyzer.output.title_features_csv_writer import TitleFeaturesCsvWriter


def create_record(
  video_id: str,
  title: str
) -> TitleFeatureRecord:
  return TitleFeatureRecord(
    video_id=video_id,
    title=title,
    video_type="long",
    length=len(title),
    word_count=4,
    mean_contextual_surprisal=5.1,
    proper_noun_ratio=0.25,
    number_count=1,
    unigram_cross_entropy=8.2,
    ctr=5.2,
    average_percentage_viewed=60.0,
    stayed_to_watch=None,
    engaged_views=None
  )


class TitleFeaturesCsvWriterTest(unittest.TestCase):
  def setUp(self):
    self.writer = TitleFeaturesCsvWriter()
    self.temporary_directory = tempfile.TemporaryDirectory()
    self.path = (
      Path(self.temporary_directory.name)
      / "nested"
      / "title_features.csv"
    )

  def tearDown(self):
    self.temporary_directory.cleanup()

  def _read_rows(self) -> list[dict[str, str]]:
    with self.path.open(
      "r",
      encoding="utf-8",
      newline=""
    ) as file:
      return list(
        csv.DictReader(file)
      )

  def test_write_creates_csv_with_header_and_records(self):
    self.writer.write(
      path=self.path,
      records=[
        create_record("video-1", "タイトル1"),
        create_record("video-2", "タイトル2")
      ]
    )

    rows = self._read_rows()

    self.assertEqual(
      len(rows),
      2
    )
    self.assertEqual(
      rows[0]["video_id"],
      "video-1"
    )
    self.assertEqual(
      rows[0]["title"],
      "タイトル1"
    )
    self.assertEqual(
      list(rows[0].keys()),
      list(TitleFeaturesCsvWriter.FIELD_NAMES)
    )

  def test_write_recreates_entire_csv_when_upsert_is_false(self):
    self.writer.write(
      path=self.path,
      records=[
        create_record("old-video", "旧タイトル")
      ]
    )

    self.writer.write(
      path=self.path,
      records=[
        create_record("video-1", "タイトル1"),
        create_record("video-2", "タイトル2")
      ],
      upsert=False
    )

    rows = self._read_rows()

    self.assertEqual(
      [row["video_id"] for row in rows],
      ["video-1", "video-2"]
    )

  def test_write_replaces_existing_video_when_upsert_is_true(self):
    self.writer.write(
      path=self.path,
      records=[
        create_record("video-1", "変更前"),
        create_record("video-2", "そのまま")
      ]
    )

    self.writer.write(
      path=self.path,
      records=[
        create_record("video-1", "変更後")
      ],
      upsert=True
    )

    rows = self._read_rows()

    self.assertEqual(
      len(rows),
      2
    )

    rows_by_video_id = {
      row["video_id"]: row
      for row in rows
    }

    self.assertEqual(
      rows_by_video_id["video-1"]["title"],
      "変更後"
    )
    self.assertEqual(
      rows_by_video_id["video-2"]["title"],
      "そのまま"
    )

  def test_write_adds_new_video_when_upsert_is_true(self):
    self.writer.write(
      path=self.path,
      records=[
        create_record("video-1", "タイトル1")
      ]
    )

    self.writer.write(
      path=self.path,
      records=[
        create_record("video-2", "タイトル2")
      ],
      upsert=True
    )

    rows = self._read_rows()

    self.assertEqual(
      [row["video_id"] for row in rows],
      ["video-1", "video-2"]
    )


if __name__ == "__main__":
  unittest.main()
