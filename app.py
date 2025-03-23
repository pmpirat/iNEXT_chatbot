from flask import Flask, render_template, request, jsonify
from chatbot import ConversationalAI

app = Flask(__name__)
bot = ConversationalAI()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message')
    response = bot.respond(user_input)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
