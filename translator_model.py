# translator_model.py
from transformers import MarianMTModel, MarianTokenizer

class TranslatorModel:
    """
    Clase para manejar el modelo de traducción y la traducción de texto.
    """
    def __init__(self, model_name='Helsinki-NLP/opus-mt-en-es', max_length=512):
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name)
        self.max_length = max_length

    def translate(self, text):
        """
        Traduce el texto, dividiéndolo en fragmentos si excede la longitud máxima.
        """
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=self.max_length)
        
        if inputs["input_ids"].shape[1] > self.max_length:
            sentences = text.split(". ")
            translated_text = ""
            
            for sentence in sentences:
                if sentence:
                    inputs = self.tokenizer(sentence, return_tensors="pt", padding=True, truncation=True, max_length=self.max_length)
                    translated = self.model.generate(**inputs)
                    translated_text += self.tokenizer.decode(translated[0], skip_special_tokens=True) + " "
                    
            return translated_text.strip()
        
        translated = self.model.generate(**inputs)
        return self.tokenizer.decode(translated[0], skip_special_tokens=True)
