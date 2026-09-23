import json
from dataclasses import asdict
from pathlib import Path

from ..analysis.result import LongAnalysisResult, ShortAnalysisResult


class AnalysisJsonWriter:
  def write(
    self,
    path: Path,
    result: LongAnalysisResult | ShortAnalysisResult
  ) -> None:
    path.parent.mkdir(
      parents=True,
      exist_ok=True
    )

    with path.open(
      "w",
      encoding="utf-8"
    ) as file:
      json.dump(
        asdict(result),
        file,
        ensure_ascii=False,
        indent=2
      )
      file.write("\n")
