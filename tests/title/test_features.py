import unittest

from src.yt_analyzer.title.features import TitleFeatures
from src.yt_analyzer.title.tokenizer import Token


def token(
  surface: str,
  pos0: str,
  pos1: str,
  normalized_form: str | None = None,
) -> Token:
  return Token(
    surface=surface,
    normalized_form=normalized_form or surface,
    dictionary_form=surface,
    part_of_speech=(pos0, pos1, "*", "*", "*", "*"),
  )


class TitleFeaturesTest(unittest.TestCase):
  def setUp(self):
    self.title = "神戸の観光！"
    self.tokens = [
      token("神戸", "名詞", "固有名詞"),
      token("の", "助詞", "格助詞"),
      token("観光", "名詞", "普通名詞"),
      token("！", "補助記号", "句点"),
    ]
    self.features = TitleFeatures(self.title, self.tokens)

  def test_length(self):
    self.assertEqual(self.features.length, len(self.title))

  def test_words_excludes_symbols(self):
    self.assertEqual(
      [word.surface for word in self.features.words],
      ["神戸", "の", "観光"],
    )

  def test_word_count(self):
    self.assertEqual(self.features.word_count, 3)

  def test_proper_noun(self):
    self.assertEqual(
      [word.surface for word in self.features.proper_noun],
      ["神戸"],
    )

  def test_proper_noun_count(self):
    self.assertEqual(self.features.proper_noun_count, 1)

  def test_proper_noun_ratio(self):
    self.assertAlmostEqual(self.features.proper_noun_ratio, 1 / 3)

  def test_proper_noun_ratio_is_zero_when_no_words(self):
    features = TitleFeatures(
      title="！",
      tokens=[token("！", "補助記号", "句点")],
    )

    self.assertEqual(features.proper_noun_ratio, 0.0)


if __name__ == "__main__":
  unittest.main()
