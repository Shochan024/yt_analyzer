import json
from dataclasses import asdict
from pathlib import Path

from ..instagram.analysis import InstagramAnalysisResult


class InstagramAnalysisJsonWriter:
  def write(
    self,
    path: Path,
    results: dict[str, InstagramAnalysisResult]
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
        {
          post_type: asdict(result)
          for post_type, result in results.items()
        },
        file,
        ensure_ascii=False,
        indent=2
      )
      file.write("\n")
