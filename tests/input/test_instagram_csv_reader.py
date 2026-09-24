import tempfile
import unittest
from pathlib import Path

from src.yt_analyzer.input.instagram_csv_reader import InstagramCsvReader
from src.yt_analyzer.instagram.model import InstagramPostType


class InstagramCsvReaderTest(unittest.TestCase):
  def test_reads_meta_export_csv(self):
    content = (
      "投稿ID,アカウントID,アカウントのユーザーネーム,アカウント名,説明,"
      "時間(秒),公開時間,リンク,投稿タイプ,データコメント,日時,ビュー,"
      "リーチ,いいね！の数,シェア数,フォロー数,コメント数,保存数\n"
      "1788,1,user,name,神戸あるある,38,09/22/2026 23:48,"
      "https://example.com,IGリール動画,,通算,105375,70894,448,47,122,136,149\n"
    )

    with tempfile.TemporaryDirectory() as directory:
      path = Path(directory) / "instagram.csv"
      path.write_text(
        content,
        encoding="utf-8"
      )

      records = InstagramCsvReader().read(path)

    self.assertEqual(len(records), 1)
    record = records[0]
    self.assertEqual(record.post_id, "1788")
    self.assertEqual(record.post_type, InstagramPostType.REEL)
    self.assertEqual(record.duration_seconds, 38)
    self.assertEqual(record.reach, 70894)
    self.assertEqual(record.likes, 448)
    self.assertEqual(record.published_at.year, 2026)

  def test_rejects_unknown_post_type(self):
    content = (
      "投稿ID,説明,公開時間,投稿タイプ,ビュー,リーチ,いいね！の数,"
      "シェア数,フォロー数,コメント数,保存数\n"
      "1,caption,09/22/2026 23:48,Unknown,1,1,1,1,1,1,1\n"
    )

    with tempfile.TemporaryDirectory() as directory:
      path = Path(directory) / "instagram.csv"
      path.write_text(
        content,
        encoding="utf-8"
      )

      with self.assertRaises(ValueError):
        InstagramCsvReader().read(path)


if __name__ == "__main__":
  unittest.main()
