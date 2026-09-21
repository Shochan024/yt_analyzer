# src/yt_analyzer/title/analyzer.py

from .features import TitleFeatures
from .tokenizer import TitleTokenizer


class TitleAnalyzer:
  def __init__(self) -> None:
    self._tokenizer = TitleTokenizer()

  def analyze(self, title: str) -> TitleFeatures:
    tokens = self._tokenizer.tokenize(title)

    return TitleFeatures(
      title=title,
      tokens=tokens
    )
