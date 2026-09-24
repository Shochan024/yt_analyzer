import csv
from datetime import datetime
from pathlib import Path
from typing import ClassVar
from zoneinfo import ZoneInfo

from ..instagram.model import InstagramPostRecord, InstagramPostType


class InstagramCsvReader:
  POST_TYPES: ClassVar[dict[str, InstagramPostType]] = {
    "Instagram画像": InstagramPostType.IMAGE,
    "Instagramカルーセル": InstagramPostType.CAROUSEL,
    "IGリール動画": InstagramPostType.REEL
  }

  REQUIRED_FIELDS = (
    "投稿ID",
    "説明",
    "公開時間",
    "投稿タイプ",
    "ビュー",
    "リーチ",
    "いいね！の数",
    "シェア数",
    "フォロー数",
    "コメント数",
    "保存数"
  )

  def read(self, path: Path) -> list[InstagramPostRecord]:
    with path.open(
      "r",
      encoding="utf-8-sig",
      newline=""
    ) as file:
      reader = csv.DictReader(file)
      self._validate_fields(reader.fieldnames or [])

      return [
        self._record(row)
        for row in reader
      ]

  def _record(self, row: dict[str, str]) -> InstagramPostRecord:
    post_type_name = self._text(row.get("投稿タイプ"))

    try:
      post_type = self.POST_TYPES[post_type_name]
    except KeyError as error:
      raise ValueError(
        f"Unsupported Instagram post type: {post_type_name}"
      ) from error

    return InstagramPostRecord(
      post_id=self._text(row.get("投稿ID")),
      caption=self._text(row.get("説明")),
      post_type=post_type,
      published_at=datetime.strptime(
        self._text(row.get("公開時間")),
        "%m/%d/%Y %H:%M"
      ).replace(
        tzinfo=ZoneInfo("Asia/Tokyo")
      ),
      link=self._optional_text(row.get("リンク")),
      duration_seconds=self._integer(row.get("時間(秒)")),
      views=self._integer(row.get("ビュー")),
      reach=self._integer(row.get("リーチ")),
      likes=self._integer(row.get("いいね！の数")),
      shares=self._integer(row.get("シェア数")),
      follows=self._integer(row.get("フォロー数")),
      comments=self._integer(row.get("コメント数")),
      saves=self._integer(row.get("保存数"))
    )

  def _validate_fields(self, fields: list[str]) -> None:
    missing = [
      field
      for field in self.REQUIRED_FIELDS
      if field not in fields
    ]

    if missing:
      raise ValueError(
        "Instagram CSV fields are missing: "
        + ", ".join(missing)
      )

  def _text(self, value: str | None) -> str:
    return (value or "").strip()

  def _optional_text(self, value: str | None) -> str | None:
    normalized = self._text(value)
    return normalized or None

  def _integer(self, value: str | None) -> int | None:
    normalized = self._text(value)

    if not normalized:
      return None

    return int(float(normalized))
