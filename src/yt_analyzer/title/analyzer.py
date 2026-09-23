# src/yt_analyzer/title/analyzer.py

from .contextual_surprisal import ContextualSurprisal
from .features import TitleFeatures
from .tokenizer import TitleTokenizer
from .word_frequency import WordFrequencyEstimator


class TitleAnalyzer:
  def __init__(
    self,
    contextual_surprisal: ContextualSurprisal | None = None,
    word_frequency_estimator: WordFrequencyEstimator | None = None
  ) -> None:
    self._tokenizer = TitleTokenizer()
    self._contextual_surprisal = contextual_surprisal
    self._word_frequency_estimator = word_frequency_estimator

  def analyze(self, title: str) -> TitleFeatures:
    tokens = self._tokenizer.tokenize(
      title
    )

    contextual_result = (
      self._contextual_surprisal.analyze(
        title
      )
      if self._contextual_surprisal
      else None
    )

    return TitleFeatures(
      title=title,
      tokens=tokens,
      word_frequency_estimator=self._word_frequency_estimator,
      mean_contextual_surprisal=(
        contextual_result.mean
        if contextual_result is not None
        else None
      ),
      contextual_top_tokens=(
        contextual_result.top_tokens
        if contextual_result is not None
        else ()
      )
    )
