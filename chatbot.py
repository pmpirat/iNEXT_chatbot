import json
import os
import difflib
from openai import OpenAI
import spacy
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Model pro vektorové porovnání
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Nastav svůj OpenAI klíč
client = OpenAI(api_key="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")  # Zkráceno pro bezpečnost

# Načti NLP model
nlp = spacy.load("en_core_web_sm")


class ConversationalAI:
    def __init__(self, memory_file='conversation_memory.json'):
        self.memory_file = memory_file
        self.memory = self.load_memory()

    def load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_memory(self):
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)

    def find_best_match(self, user_input):
        user_input = user_input.lower()
        matches = difflib.get_close_matches(user_input, self.memory.keys(), n=1, cutoff=0.6)
        if matches:
            return matches[0]
        return None

    def generate_response_with_gpt(self, user_input):
        # Vytvoří prompt z naučených znalostí
        knowledge_context = "\n".join([f"Q: {q}\nA: {a}" for q, a in self.memory.items()])

        prompt = f"""
Jsi chytrý chatbot, který se učí z komunikace. Tady jsou znalosti, které jsi nasbíral:
{knowledge_context}

Nyní odpověz na následující otázku:
Q: {user_input}
A:"""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Jsi přátelský a chytrý český chatbot, který se učí z rozhovorů."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Chyba OpenAI API]: {e}"

    def respond(self, user_input):
        user_input_clean = user_input.strip().lower()

        if user_input_clean.startswith("learn:"):
            try:
                parts = user_input_clean[6:].split("=>")
                question = parts[0].strip()
                answer = parts[1].strip()
                self.memory[question] = answer
                self.save_memory()
                return f"Učím se: '{question}' => '{answer}'"
            except:
                return "Použij formát: learn: otázka => odpověď"

        # Pokud zná odpověď – použije vlastní znalosti
        match = self.find_best_match(user_input_clean)
        if match:
            return self.memory[match]

        # Pokud nezná – vygeneruje odpověď pomocí GPT
        gpt_response = self.generate_response_with_gpt(user_input)
        # Naučí se tuto novou frázi, aby příště už odpověděl sám
        self.memory[user_input_clean] = gpt_response
        self.save_memory()
        return gpt_response


# Pomocná funkce pro vektorový embedding (zatím nevyužitá)
def get_embedding(text):
    return model.encode(text)


# Spuštění
if __name__ == "__main__":
    bot = ConversationalAI()

    print("Chatbot: Ahoj! Mluv se mnou. (napiš 'konec' pro ukončení)")
