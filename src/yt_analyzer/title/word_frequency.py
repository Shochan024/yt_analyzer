# src/yt_analyzer/title/word_frequency.py

from wordfreq import word_frequency


class WordFrequencyEstimator:
  MINIMUM_PROBABILITY = 1e-9

  def __init__(self, language: str = "ja") -> None:
    self._language = language

  def probability(self, word: str) -> float:
    return float(
      word_frequency(
        word,
        self._language,
        minimum=self.MINIMUM_PROBABILITY
      )
    )
