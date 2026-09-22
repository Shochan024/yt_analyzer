# src/yt_analyzer/config/settings.py

import os
from pathlib import Path


class Settings:
  @property
  def spreadsheet_id(self) -> str:
    return self._required(
      "YT_ANALYZER_SPREADSHEET_ID"
    )

  @property
  def google_credentials(self) -> str:
    return self._required(
      "YT_ANALYZER_GOOGLE_CREDENTIALS"
    )

  @property
  def contextual_model(self) -> str:
    return self._required(
      "YT_ANALYZER_CONTEXTUAL_MODEL"
    )

  @property
  def output_dir(self) -> Path:
    return Path(
      os.getenv(
        "YT_ANALYZER_OUTPUT_DIR",
        "output"
      )
    )

  def _required(self, name: str) -> str:
    value = os.getenv(
      name
    )

    if value is None or not value.strip():
      raise ValueError(
        f"Environment variable is required: {name}"
      )

    return value.strip()
