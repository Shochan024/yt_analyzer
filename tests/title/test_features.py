import math
import unittest

from src.yt_analyzer.title.features import TitleFeatures
from src.yt_analyzer.title.tokenizer import Token


def create_token(surface: str, pos0: str, pos1: str) -> Token:
  return Token(
    surface=surface,
    normalized_form=surface,
    dictionary_form=surface,
    part_of_speech=(pos0, pos1, "*", "*", "*", "*")
  )


class FakeWordFrequencyEstimator:
  def __init__(self, probabilities: dict[str, float]) -> None:
    self._probabilities = probabilities

  def probability(self, word: str) -> float:
    return self._probabilities.get(word, 1e-9)


class TitleFeaturesTest(unittest.TestCase):
  def setUp(self):
    self.title = "神戸の観光！"
    self.tokens = [
      create_token("神戸", "名詞", "固有名詞"),
      create_token("の", "助詞", "格助詞"),
      create_token("観光", "名詞", "普通名詞"),
      create_token("！", "補助記号", "句点")
    ]
    self.features = TitleFeatures(
      title=self.title,
      tokens=self.tokens
    )

  def test_length(self):
    self.assertEqual(
      self.features.length,
      len(self.title)
    )

  def test_words_excludes_symbols(self):
    self.assertEqual(
      [token.surface for token in self.features.words],
      ["神戸", "の", "観光"]
    )

  def test_word_count(self):
    self.assertEqual(
      self.features.word_count,
      3
    )

  def test_proper_noun(self):
    self.assertEqual(
      [token.surface for token in self.features.proper_noun],
      ["神戸"]
    )

  def test_proper_nouns_returns_unique_surfaces(self):
    features = TitleFeatures(
      title="神戸神戸観光",
      tokens=[
        create_token("神戸", "名詞", "固有名詞"),
        create_token("神戸", "名詞", "固有名詞"),
        create_token("観光", "名詞", "普通名詞")
      ]
    )

    self.assertEqual(
      features.proper_nouns,
      ("神戸",)
    )

  def test_proper_noun_count(self):
    self.assertEqual(
      self.features.proper_noun_count,
      1
    )

  def test_proper_noun_ratio(self):
    self.assertAlmostEqual(
      self.features.proper_noun_ratio,
      1 / 3
    )

  def test_proper_noun_ratio_is_zero_when_no_words(self):
    features = TitleFeatures(
      title="！",
      tokens=[
        create_token("！", "補助記号", "句点")
      ]
    )

    self.assertEqual(
      features.proper_noun_ratio,
      0.0
    )

  def test_unique_word_count(self):
    features = TitleFeatures(
      title="神戸神戸観光",
      tokens=[
        create_token("神戸", "名詞", "固有名詞"),
        create_token("神戸", "名詞", "固有名詞"),
        create_token("観光", "名詞", "普通名詞")
      ]
    )

    self.assertEqual(
      features.unique_word_count,
      2
    )

  def test_unique_word_ratio(self):
    features = TitleFeatures(
      title="神戸神戸観光",
      tokens=[
        create_token("神戸", "名詞", "固有名詞"),
        create_token("神戸", "名詞", "固有名詞"),
        create_token("観光", "名詞", "普通名詞")
      ]
    )

    self.assertAlmostEqual(
      features.unique_word_ratio,
      2 / 3
    )

  def test_number_count(self):
    features = TitleFeatures(
      title="2026年に行きたい観光地10選",
      tokens=[]
    )

    self.assertEqual(
      features.number_count,
      2
    )

  def test_number_count_is_zero_when_no_number(self):
    features = TitleFeatures(
      title="神戸のおすすめ観光地",
      tokens=[]
    )

    self.assertEqual(
      features.number_count,
      0
    )

  def test_unigram_top_words_returns_highest_scores(self):
    tokens = [
      create_token("神戸", "名詞", "固有名詞"),
      create_token("観光", "名詞", "普通名詞"),
      create_token("旅行", "名詞", "普通名詞"),
      create_token("温泉", "名詞", "普通名詞")
    ]

    estimator = FakeWordFrequencyEstimator({
      "神戸": 0.01,
      "観光": 0.1,
      "旅行": 0.001,
      "温泉": 0.005
    })

    features = TitleFeatures(
      title="神戸観光旅行温泉",
      tokens=tokens,
      word_frequency_estimator=estimator
    )

    self.assertEqual(
      [item.text for item in features.unigram_top_words],
      ["旅行", "温泉", "神戸"]
    )
    self.assertGreater(
      features.unigram_top_words[0].score,
      features.unigram_top_words[1].score
    )

  def test_unigram_cross_entropy(self):
    tokens = [
      create_token("神戸", "名詞", "固有名詞"),
      create_token("観光", "名詞", "普通名詞")
    ]

    estimator = FakeWordFrequencyEstimator({
      "神戸": 0.01,
      "観光": 0.005
    })

    features = TitleFeatures(
      title="神戸観光",
      tokens=tokens,
      word_frequency_estimator=estimator
    )

    expected = (
      -math.log(0.01)
      - math.log(0.005)
    ) / 2

    self.assertAlmostEqual(
      features.unigram_cross_entropy,
      expected
    )

  def test_unigram_cross_entropy_with_unknown_word(self):
    estimator = FakeWordFrequencyEstimator({})

    features = TitleFeatures(
      title="未知語",
      tokens=[
        create_token("未知語", "名詞", "普通名詞")
      ],
      word_frequency_estimator=estimator
    )

    expected = -math.log(1e-9)

    self.assertAlmostEqual(
      features.unigram_cross_entropy,
      expected
    )

  def test_unigram_cross_entropy_is_zero_without_word_frequency_estimator(self):
    features = TitleFeatures(
      title="神戸",
      tokens=[
        create_token("神戸", "名詞", "固有名詞")
      ]
    )

    self.assertEqual(
      features.unigram_cross_entropy,
      0.0
    )

  def test_mean_contextual_surprisal(self):
    features = TitleFeatures(
      title="神戸の観光",
      tokens=[],
      mean_contextual_surprisal=6.1
    )

    self.assertEqual(
      features.mean_contextual_surprisal,
      6.1
    )

  def test_mean_contextual_surprisal_is_zero_when_not_given(self):
    features = TitleFeatures(
      title="神戸の観光",
      tokens=[]
    )

    self.assertEqual(
      features.mean_contextual_surprisal,
      0.0
    )
