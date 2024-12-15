from transformers import AutoModelForCausalLM, AutoTokenizer


class LLaMAUtils:
    def __init__(self, model_path="./llama_model"):
        """
        Initialize the LLaMA model and tokenizer.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path)

    def translate(self, text, target_language="en"):
        """
        Translate text to the target language using LLaMA.

        :param text: The input text to translate.
        :param target_language: The target language ('en' for English, 'ja' for Japanese, etc.).
        :return: Translated text.
        """
        prompt = f"Translate the following text to {target_language}:\n{text}"
        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids
        outputs = self.model.generate(input_ids, max_length=200, num_return_sequences=1)
        translated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return translated_text

    def summarize(self, text):
        """
        Generate a summary of the input text using LLaMA.

        :param text: The input text to summarize.
        :return: A summarized version of the text.
        """
        prompt = f"Summarize the following text:\n{text}"
        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids
        outputs = self.model.generate(input_ids, max_length=150, num_return_sequences=1)
        summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return summary
