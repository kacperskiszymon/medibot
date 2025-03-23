from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from chatbot import get_bot_response
from booking import make_booking
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_message = request.json.get("message")
    response = get_bot_response(user_message)
    return jsonify({"response": response})

@app.route('/book', methods=['POST'])
def book():
    data = request.json
    booking_status = make_booking(data)
    return jsonify(booking_status)

if __name__ == '__main__':
    app.run(debug=True)
