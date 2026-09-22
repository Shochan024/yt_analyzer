import json
import tempfile
import unittest
from pathlib import Path

from src.yt_analyzer.analysis.result import (
  CorrelationResult,
  LongAnalysisResult,
  RegressionResult
)
from src.yt_analyzer.output.analysis_json_writer import AnalysisJsonWriter


class AnalysisJsonWriterTest(unittest.TestCase):
  def test_write_serializes_nested_analysis_result(self):
    result = LongAnalysisResult(
      correlations={
        "length": CorrelationResult(
          feature_name="length",
          target_name="ctr",
          pearson=0.5,
          pearson_p_value=0.1,
          spearman=0.4,
          spearman_p_value=0.2,
          sample_size=3
        )
      },
      regressions={
        "length": RegressionResult(
          feature_name="length",
          target_name="ctr",
          coefficient=0.01,
          intercept=0.1,
          r_squared=0.25,
          p_value=0.1,
          standard_error=0.02,
          sample_size=3
        )
      },
      sample_size=3
    )

    with tempfile.TemporaryDirectory() as directory:
      path = Path(directory) / "long_analysis.json"
      AnalysisJsonWriter().write(path, result)
      data = json.loads(path.read_text(encoding="utf-8"))

    self.assertEqual(data["sample_size"], 3)
    self.assertEqual(
      data["correlations"]["length"]["pearson"],
      0.5
    )
    self.assertEqual(
      data["regressions"]["length"]["r_squared"],
      0.25
    )


if __name__ == "__main__":
  unittest.main()
