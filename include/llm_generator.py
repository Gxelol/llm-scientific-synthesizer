from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class LLMGenerator:
    def __init__(self, model_name="gpt2"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        if torch.cuda.is_available():
            self.model = self.model.to('cuda')

    def generate_summary(self, relevant_texts):
        combined_text = "\n\n".join(relevant_texts)
        
        inputs = self.tokenizer(combined_text, return_tensors="pt", truncation=True, padding=True, max_length=1024)
        
        if torch.cuda.is_available():
            inputs = {key: value.to('cuda') for key, value in inputs.items()}
        
        output = self.model.generate(**inputs, max_length=500, num_beams=5, no_repeat_ngram_size=2, early_stopping=True)

        summary = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return summary
