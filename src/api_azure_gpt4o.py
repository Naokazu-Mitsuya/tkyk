import requests
import json
import argparse
from elasticsearch import Elasticsearch  # Elasticsearchを例として使用

# 引数の設定
parser = argparse.ArgumentParser(description="Analyze contract risks using Azure GPT-4 model with RAG.")
parser.add_argument('--file_path', type=str, required=True, help="Path to the text file containing contract data.")
parser.add_argument('--max_tokens', type=int, default=800, help="Maximum number of tokens to generate.")
parser.add_argument('--prompt_path', type=str, default=None, help="Path to the text file containing the prompt.")
args = parser.parse_args()

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

# 契約書データの読み込み（引数からパスを受け取る）
with open(args.file_path) as f:
    contract_text = f.read().strip()

# プロンプトの読み込み
if args.prompt_path:
    with open(args.prompt_path) as pf:
        prompt = pf.read().strip()
else:
    prompt = "analyze risk on this contract as a user: "

# Elasticsearchを使用して関連するドキュメントを検索
es = Elasticsearch("http://localhost:9200")  # Elasticsearchのインスタンスに接続

# 検索クエリの設定
query = {
    "query": {
        "match": {
            "content": contract_text  # 契約書に関連する情報を検索
        }
    }
}

# 検索結果を取得
search_results = es.search(index="legal_documents", body=query)
retrieved_docs = search_results['hits']['hits'][:3]  # 上位3件のドキュメントを取得

# 検索結果をプロンプトに組み込む
retrieved_text = "\n".join([doc['_source']['content'] for doc in retrieved_docs])
full_prompt = f"{prompt}\n\nContext from related legal documents:\n{retrieved_text}\n\nContract:\n{contract_text}"

# リクエストペイロードの設定（検索結果を組み込む）
payload = {
    "messages": [{"role":"user", "content": full_prompt}],
    "temperature": 0.7,
    "max_tokens": args.max_tokens,
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