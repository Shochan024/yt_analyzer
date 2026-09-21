# tests/title/test_tokenizer.py

import unittest

from src.yt_analyzer.title.tokenizer import TitleTokenizer, Token


class TokenTest(unittest.TestCase):
  def test_is_proper_noun(self):
    token = Token(
      surface="神戸",
      normalized_form="神戸",
      dictionary_form="神戸",
      part_of_speech=("名詞", "固有名詞", "地名", "一般", "*", "*"),
    )

    self.assertTrue(token.is_proper_noun)

  def test_is_not_proper_noun(self):
    token = Token(
      surface="観光",
      normalized_form="観光",
      dictionary_form="観光",
      part_of_speech=("名詞", "普通名詞", "一般", "*", "*", "*"),
    )

    self.assertFalse(token.is_proper_noun)

  def test_is_symbol(self):
    token = Token(
      surface="！",
      normalized_form="!",
      dictionary_form="！",
      part_of_speech=("補助記号", "句点", "*", "*", "*", "*"),
    )

    self.assertTrue(token.is_symbol)


class TitleTokenizerTest(unittest.TestCase):
  def setUp(self):
    self.tokenizer = TitleTokenizer()

  def test_tokenize_returns_tokens(self):
    tokens = self.tokenizer.tokenize("神戸の観光")

    self.assertGreater(len(tokens), 0)
    self.assertTrue(all(isinstance(token, Token) for token in tokens))

  def test_tokenize_preserves_surface_text(self):
    title = "神戸の観光"
    tokens = self.tokenizer.tokenize(title)

    self.assertEqual(
      "".join(token.surface for token in tokens),
      title,
    )
