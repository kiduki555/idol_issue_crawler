import unittest
from src.data_preprocessing.preprocess import clean_text, preprocess_data
from src.data_preprocessing.scoring import calculate_score
from src.data_preprocessing.llama_utils import LLaMAUtils

class TestDataPreprocessing(unittest.TestCase):
    def test_clean_text(self):
        text = "<b>Hello</b> World! #Python"
        cleaned = clean_text(text)
        self.assertEqual(cleaned, "Hello World!", "Text should be cleaned.")

    def test_preprocess_data(self):
        data = {"title": "<b>Title</b>", "content": "Content with <i>HTML</i>."}
        preprocessed = preprocess_data(data)
        self.assertEqual(preprocessed["title"], "Title", "Title should be cleaned.")
        self.assertEqual(preprocessed["content"], "Content with HTML.", "Content should be cleaned.")

    def test_calculate_score(self):
        score = calculate_score(view_count=1000, comment_count=50, sentiment_score=0.8)
        self.assertTrue(score > 0, "Score should be calculated correctly.")

    def test_llama_translate(self):
        llama = LLaMAUtils(model_path="./llama_model")
        translated = llama.translate("안녕하세요", target_language="en")
        self.assertIsInstance(translated, str, "Translation should return a string.")

if __name__ == "__main__":
    unittest.main()
