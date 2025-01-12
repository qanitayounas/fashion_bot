from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import pymongo
from pymongo import MongoClient
import pandas as pd
import traceback
from llm import generate_response, load_fashion_data

app = Flask(__name__)
CORS(app)

# MongoDB Connection
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Fashion']
    history_collection = db['History']
    print("Successfully connected to MongoDB")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# Load the fashion dataset
fashion_data_path = "./fashion_data.xls"
fashion_data = load_fashion_data(fashion_data_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not request.is_json:
            return jsonify({'error': 'Invalid input, JSON expected'}), 400

        user_message = request.json.get('message', '').strip().lower()
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400

        # Handle greetings separately
        if user_message in ['hi', 'hello', 'hey']:
            response = "Hello! How can I help you today?"
        else:
            response = generate_response(user_message, fashion_data)
            if not response:
                response = "Sorry, I couldn't process your request."

        # Store conversation history
        conversation_entry = {"user": user_message, "ai": response}
        history_collection.insert_one(conversation_entry)

        return jsonify({'message': response})

    except Exception as e:
        print(f"Error in chat route: {e}")
        print(traceback.format_exc())
        return jsonify({'error': 'An error occurred while processing your request'}), 500

@app.route('/history', methods=['GET'])
def history():
    try:
        history_entries = list(history_collection.find({}, {"_id": 0, "user": 1, "ai": 1}))
        return jsonify(history_entries)
    except Exception as e:
        print(f"Error in history route: {e}")
        return jsonify({'error': 'Error fetching history'}), 500

@app.route('/history/<int:index>', methods=['GET'])
def history_detail(index):
    try:
        history_entries = list(history_collection.find({}, {"_id": 0}))
        if 0 <= index < len(history_entries):
            return jsonify(history_entries[index])
        return jsonify({'error': 'Invalid index'}), 404
    except Exception as e:
        print(f"Error in history_detail route: {e}")
        return jsonify({'error': 'Error fetching history entry'}), 500

if __name__ == "__main__":
    app.run(debug=True)