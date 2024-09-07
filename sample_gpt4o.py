import requests
import json

# APIキーの読み込み
with open('/root/azure_gpt4o_key.txt') as f:
    key = f.read().strip()


# APIエンドポイントの設定
base_url = "https://aoai-ump-just-eastus.openai.azure.com/openai/deployments/aoai-gpt-4o/chat/completions?api-version=2023-05-15"

# リクエストヘッダーの設定
headers = {
    'api-key': key,
    'Content-Type': 'application/json'
}

# 契約書データの読み込み
with open('/mnt/bereal.txt') as f:
    text = f.read().strip()

# リクエストペイロードの設定
payload = {
    "messages": [{"role":"user", "content": "analyze risk on this contract as a user: " + text}],
    "temperature": 0.7,
    "max_tokens": 800,
    "top_p": 0.95,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "stop": None
}

# APIリクエスト
response = requests.post(base_url, headers=headers, data=json.dumps(payload))

# レスポンスの表示
if response.status_code == 200:
    result = response.json()
    print(result['choices'][0]['message']['content'].strip())
else:
    print(f"Error: {response.status_code}")
    print(response.text)