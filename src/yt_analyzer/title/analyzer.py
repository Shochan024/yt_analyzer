# src/yt_analyzer/title/analyzer.py

from .contextual_surprisal import ContextualSurprisal
from .features import TitleFeatures
from .tokenizer import TitleTokenizer


class TitleAnalyzer:
  def __init__(
    self,
    contextual_surprisal: ContextualSurprisal | None = None,
  ) -> None:
    self._tokenizer = TitleTokenizer()
    self._contextual_surprisal = contextual_surprisal

  def analyze(
    self,
    title: str,
    word_frequencies: dict[str, int] | None = None
  ) -> TitleFeatures:
    tokens = self._tokenizer.tokenize(title)

    mean_contextual_surprisal = (
      self._contextual_surprisal.mean(title)
      if self._contextual_surprisal
      else None
    )

    return TitleFeatures(
      title=title,
      tokens=tokens,
      word_frequencies=word_frequencies,
      mean_contextual_surprisal=mean_contextual_surprisal
    )
