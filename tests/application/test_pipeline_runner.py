import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from src.yt_analyzer.application.pipeline_runner import PipelineRunner


class PipelineRunnerTest(unittest.TestCase):
  def test_run_executes_steps_in_order_and_returns_outputs(self):
    calls = []

    def first():
      calls.append("first")
      return Path("output/first.csv")

    def second():
      calls.append("second")
      return Path("output/second.json")

    runner = PipelineRunner(
      steps=[
        ("First step", first),
        ("Second step", second)
      ]
    )

    with redirect_stdout(io.StringIO()) as output:
      paths = runner.run()

    self.assertEqual(calls, ["first", "second"])
    self.assertEqual(
      paths,
      [
        Path("output/first.csv"),
        Path("output/second.json")
      ]
    )
    self.assertEqual(
      output.getvalue(),
      "First step...\n"
      "Written: output/first.csv\n"
      "Second step...\n"
      "Written: output/second.json\n"
      "Done.\n"
    )

  def test_run_stops_when_step_raises(self):
    calls = []

    def first():
      calls.append("first")
      return Path("output/first.csv")

    def failing():
      calls.append("failing")
      raise RuntimeError("failed")

    def never():
      calls.append("never")
      return Path("output/never.json")

    runner = PipelineRunner(
      steps=[
        ("First step", first),
        ("Failing step", failing),
        ("Never step", never)
      ]
    )

    with self.assertRaisesRegex(
      RuntimeError,
      "failed"
    ):
      runner.run()

    self.assertEqual(
      calls,
      ["first", "failing"]
    )


if __name__ == "__main__":
  unittest.main()
