from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
API_KEY = os.environ.get('API_KEY')
FAST_BASE_URL = 'https://fast.typegpt.net/v1/chat/completions'
PUTER_BASE_URL = 'https://api.puter.com/chat'
VALID_MODELS = ['deepseek-r1', 'gpt-4o', 'claude']

def call_fast_typegpt(prompt, model):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 50
    }
    try:
        response = requests.post(FAST_BASE_URL, json=payload, headers=headers)
        response.raise_for_status()
        return {'success': True, 'data': response.json()['choices'][0]['message']['content']}
    except requests.RequestException as e:
        return {'success': False, 'error': str(e)}

def call_puter_ai(prompt, model):
    payload = {
        'model': model,
        'prompt': prompt,
        'stream': False
    }
    try:
        response = requests.post(PUTER_BASE_URL, json=payload)
        response.raise_for_status()
        return {'success': True, 'data': response.json().get('text', 'No response')}
    except requests.RequestException as e:
        return {'success': False, 'error': str(e)}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        prompt = data.get('prompt')
        model = data.get('model', 'deepseek-r1')

        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        if model not in VALID_MODELS:
            return jsonify({'error': f'Invalid model. Choose from: {VALID_MODELS}'}), 400

        if model == 'claude':
            result = call_puter_ai(prompt, model)
        else:
            result = call_fast_typegpt(prompt, model)

        if result['success']:
            return jsonify({'response': result['data']}), 200
        else:
            return jsonify({'error': result['error']}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, workers=4)
