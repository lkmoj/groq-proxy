from flask import Flask, request, jsonify
import requests, json, traceback

app = Flask(__name__)

OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'
DEFAULT_MODEL   = 'deepseek/deepseek-v4-flash:free'

@app.route('/')
def root():
    return 'OK'

@app.route('/ping', methods=['GET', 'POST'])
def ping():
    return 'pong'

@app.route('/ask', methods=['POST'])
def ask():
    try:
        raw = request.get_data(as_text=True)
        print(f'[ask] raw body: {raw[:300]}', flush=True)
        try:
            data = json.loads(raw)
        except Exception as e:
            return jsonify({'error': 'bad json: ' + str(e), 'raw': raw[:200]}), 400

        api_key    = data.get('key', '')
        prompt     = data.get('prompt', '')
        system     = data.get('system', '')
        model      = data.get('model', DEFAULT_MODEL)
        max_tokens = int(data.get('max_tokens', 20))

        print(f'[ask] model={model} key_len={len(api_key)} max_tokens={max_tokens}', flush=True)

        if not api_key:
            return jsonify({'error': 'no api key'}), 400

        resp = requests.post(
            OPENROUTER_URL,
            headers={
                'Authorization': 'Bearer ' + api_key,
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://github.com/lkmoj/groq-proxy',
                'X-Title': 'SAMP AI Bot'
            },
            json={
                'model': model,
                'max_tokens': max_tokens,
                'temperature': 0.7,
                'messages': [
                    {'role': 'system', 'content': system},
                    {'role': 'user',   'content': prompt}
                ]
            },
            timeout=15
        )

        print(f'[ask] openrouter status={resp.status_code} body={resp.text[:300]}', flush=True)

        result = resp.json()
        if 'choices' not in result:
            return jsonify({'error': str(result)}), 500

        answer = result['choices'][0]['message']['content']
        return jsonify({'answer': answer})

    except Exception as e:
        print(f'[ask] exception: {traceback.format_exc()}', flush=True)
        return jsonify({'error': traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
