import tempfile
import unittest
from pathlib import Path

from src.yt_analyzer.input.title_features_csv_reader import TitleFeaturesCsvReader


class TitleFeaturesCsvReaderTest(unittest.TestCase):
  def test_read_parses_records_and_blank_optional_values(self):
    with tempfile.TemporaryDirectory() as directory:
      path = Path(directory) / "title_features.csv"
      path.write_text(
        "video_id,title,video_type,length,word_count,"
        "mean_contextual_surprisal,proper_noun_ratio,number_count,"
        "unigram_cross_entropy,ctr,average_percentage_viewed,"
        "stayed_to_watch,engaged_views\n"
        "video-1,title,long,20,10,4.5,0.2,1,8.5,0.12,,,\n"
        "video-2,title,short,30,12,5.5,0.1,0,9.5,,0.42,0.65,120\n",
        encoding="utf-8"
      )

      records = TitleFeaturesCsvReader().read(path)

    self.assertEqual(len(records), 2)
    self.assertEqual(records[0].video_id, "video-1")
    self.assertEqual(records[0].video_type, "long")
    self.assertEqual(records[0].ctr, 0.12)
    self.assertIsNone(records[0].average_percentage_viewed)
    self.assertIsNone(records[0].stayed_to_watch)
    self.assertIsNone(records[0].engaged_views)
    self.assertEqual(records[1].engaged_views, 120)

  def test_read_raises_when_file_does_not_exist(self):
    path = Path("missing-title-features.csv")

    with self.assertRaisesRegex(
      FileNotFoundError,
      "Title features CSV not found"
    ):
      TitleFeaturesCsvReader().read(path)


if __name__ == "__main__":
  unittest.main()
