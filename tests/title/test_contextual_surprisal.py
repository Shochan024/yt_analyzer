# tests/title/test_contextual_surprisal.py

import unittest
from unittest.mock import Mock, patch

import torch

from src.yt_analyzer.title.contextual_surprisal import ContextualSurprisal


class ContextualSurprisalTest(unittest.TestCase):
  @patch(
    "src.yt_analyzer.title.contextual_surprisal.AutoModelForCausalLM"
  )
  @patch(
    "src.yt_analyzer.title.contextual_surprisal.T5Tokenizer"
  )
  def setUp(
    self,
    tokenizer_class,
    model_class,
  ):
    self.tokenizer = Mock()
    self.model = Mock()

    tokenizer_class.from_pretrained.return_value = self.tokenizer
    model_class.from_pretrained.return_value = self.model

    self.contextual_surprisal = ContextualSurprisal(
      model_name="dummy-model",
    )

  def test_mean_is_zero_when_text_is_empty(self):
    self.assertEqual(
      self.contextual_surprisal.mean(""),
      0.0,
    )

  def test_mean_is_zero_when_token_count_is_one(self):
    self.tokenizer.return_value = {
      "input_ids": torch.tensor([[1]]),
    }

    self.assertEqual(
      self.contextual_surprisal.mean("神戸"),
      0.0,
    )

  def test_mean_returns_average_surprisal(self):
    self.tokenizer.return_value = {
      "input_ids": torch.tensor([[0, 1, 2]]),
    }

    outputs = Mock()
    outputs.logits = torch.tensor([
      [
        [3.0, 1.0, 0.0],
        [0.0, 3.0, 1.0],
        [0.0, 0.0, 3.0],
      ]
    ])

    self.model.return_value = outputs

    result = self.contextual_surprisal.mean(
      "神戸観光",
    )

    self.assertGreater(
      result,
      0.0,
    )

  def test_analyze_returns_high_surprisal_tokens(self):
    self.tokenizer.return_value = {
      "input_ids": torch.tensor([[0, 1, 2]])
    }
    self.tokenizer.decode.side_effect = lambda token_ids, **_: {
      1: "珍語",
      2: "観光"
    }[token_ids[0]]

    outputs = Mock()
    outputs.logits = torch.tensor([
      [
        [5.0, 0.0, 0.0],
        [0.0, 0.0, 5.0],
        [0.0, 0.0, 5.0]
      ]
    ])
    self.model.return_value = outputs

    result = self.contextual_surprisal.analyze(
      "珍語観光"
    )

    self.assertEqual(
      [item.text for item in result.top_tokens],
      ["珍語", "観光"]
    )
    self.assertGreater(
      result.top_tokens[0].score,
      result.top_tokens[1].score
    )

  def test_model_is_set_to_eval_mode(self):
    self.model.eval.assert_called_once()
