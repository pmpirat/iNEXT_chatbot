import json
import os
import difflib
import openai
import spacy

# Nastav svůj OpenAI klíč
openai.api_key = "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"

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

    def ask_openai(self, prompt):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Nebo "gpt-4" pokud máš přístup
                messages=[
                    {"role": "system", "content": "Jsi nápomocný konverzační asistent."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response['choices'][0]['message']['content'].strip()
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

        # Nejprve zkusí odpovědět ze své paměti
        match = self.find_best_match(user_input_clean)
        if match:
            return self.memory[match]

        # Když neví, zeptá se GPT
        gpt_response = self.ask_openai(user_input)
        # Volitelně se může automaticky učit z odpovědi GPT
        self.memory[user_input_clean] = gpt_response
        self.save_memory()
        return gpt_response

# Spuštění
bot = ConversationalAI()

print("Chatbot: Ahoj! Mluv se mnou. (napiš 'konec' pro ukončení)")
