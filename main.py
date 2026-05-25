from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def root():
    return 'OK'

@app.route('/ping')
def ping():
    return 'pong'

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json(force=True)
        api_key = data.get('key', '')
        prompt  = data.get('prompt', '')
        system  = data.get('system', '')

        resp = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Authorization': 'Bearer ' + api_key,
                'Content-Type': 'application/json'
            },
            json={
                'model': 'llama-3.1-8b-instant',
                'max_tokens': 60,
                'temperature': 0.85,
                'messages': [
                    {'role': 'system', 'content': system},
                    {'role': 'user',   'content': prompt}
                ]
            },
            timeout=15
        )

        answer = resp.json()['choices'][0]['message']['content']
        return jsonify({'answer': answer})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
