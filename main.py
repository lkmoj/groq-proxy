from flask import Flask, request, jsonify
import requests, json, traceback

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
        # Читаем raw body и парсим сами
        raw = request.get_data(as_text=True)
        try:
            data = json.loads(raw)
        except Exception as e:
            return jsonify({'error': 'bad json: ' + str(e), 'raw': raw[:200]}), 400

        api_key = data.get('key', '')
        prompt  = data.get('prompt', '')
        system  = data.get('system', '')

        if not api_key:
            return jsonify({'error': 'no api key'}), 400

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

        result = resp.json()
        if 'choices' not in result:
            return jsonify({'error': str(result)}), 500

        answer = result['choices'][0]['message']['content']
        return jsonify({'answer': answer})

    except Exception as e:
        return jsonify({'error': traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
