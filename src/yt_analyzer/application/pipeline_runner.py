from collections.abc import Callable
from pathlib import Path


PipelineStep = tuple[
  str,
  Callable[[], Path]
]


class PipelineRunner:
  def __init__(
    self,
    steps: list[PipelineStep]
  ) -> None:
    self._steps = steps

  def run(self) -> list[Path]:
    outputs = []

    for name, step in self._steps:
      print(f"{name}...")
      output_path = step()
      print(f"Written: {output_path}")
      outputs.append(output_path)

    print("Done.")

    return outputs
