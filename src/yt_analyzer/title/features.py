# src/yt_analyzer/title/features.py

import math
import re

from .tokenizer import Token
from .word_frequency import WordFrequencyEstimator


class TitleFeatures:
  def __init__(
    self,
    title: str,
    tokens: list[Token],
    word_frequency_estimator: WordFrequencyEstimator | None = None,
    mean_contextual_surprisal: float | None = None
  ) -> None:
    self.title = title
    self.tokens = tokens
    self._word_frequency_estimator = word_frequency_estimator
    self._mean_contextual_surprisal = mean_contextual_surprisal

  @property
  def length(self) -> int:
    return len(self.title)

  @property
  def words(self) -> list[Token]:
    return [
      token
      for token in self.tokens
      if not token.is_symbol
    ]

  @property
  def word_count(self) -> int:
    return len(self.words)

  @property
  def proper_noun(self) -> list[Token]:
    return [
      token
      for token in self.words
      if token.is_proper_noun
    ]

  @property
  def proper_noun_count(self) -> int:
    return len(self.proper_noun)

  @property
  def proper_noun_ratio(self) -> float:
    if self.word_count == 0:
      return 0.0

    return (
      self.proper_noun_count
      / self.word_count
    )

  @property
  def unique_word_count(self) -> int:
    return len({
      token.normalized_form
      for token in self.words
    })

  @property
  def unique_word_ratio(self) -> float:
    if self.word_count == 0:
      return 0.0

    return (
      self.unique_word_count
      / self.word_count
    )

  @property
  def number_count(self) -> int:
    return len(
      re.findall(
        r"\d+",
        self.title
      )
    )

  @property
  def unigram_cross_entropy(self) -> float:
    if not self.words:
      return 0.0

    if self._word_frequency_estimator is None:
      return 0.0

    scores = [
      -math.log(
        self._word_frequency_estimator.probability(
          token.normalized_form
        )
      )
      for token in self.words
    ]

    return (
      sum(scores)
      / len(scores)
    )

  @property
  def mean_contextual_surprisal(self) -> float:
    return (
      self._mean_contextual_surprisal
      or 0.0
    )
