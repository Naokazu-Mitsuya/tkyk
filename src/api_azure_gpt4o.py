import os
import requests
import json
import argparse

# 引数の設定
parser = argparse.ArgumentParser(description="Analyze contract risks using Azure GPT-4 model with reflection loop.")
parser.add_argument('--file_path', type=str, required=True, help="Path to the text file containing contract data.")
parser.add_argument('--max_tokens', type=int, default=800, help="Maximum number of tokens to generate.")
parser.add_argument('--prompt_path', type=str, default=None, help="Path to the text file containing the prompt.")
parser.add_argument('--max_iterations', type=int, default=5, help="Maximum number of reflection iterations.")
parser.add_argument('--review_prompt', type=str, default=None, help="Path to the text file containing the review prompt.")
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

# 契約書データの読み込み
with open(args.file_path) as f:
    text = f.read().strip()

# プロンプトの読み込み
with open(args.prompt_path) as f:
    prompt = f.read().strip()

with open(args.review_prompt) as f:
    review_prompt = f.read().strip()

def critique_response(response_content):
    """生成された応答の批評を行う関数"""
    critique_prompt = (
        f"{review_prompt}\n\n"
        f"{response_content}"
    )
    
    payload = {
        "messages": [
            {"role": "assistant", "content": critique_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 300,
        "top_p": 0.95,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None
    }
    
    critique_response = requests.post(base_url, headers=headers, data=json.dumps(payload))
    
    if critique_response.status_code == 200:
        result = critique_response.json()
        critique = result['choices'][0]['message']['content'].strip()
        return critique
    else:
        raise Exception(f"Error during critique: {critique_response.status_code}")

def is_critique_sufficient(critique):
    """批評が十分かどうかを判定する"""
    # 批評の最後に出力された 0 か 1 をチェックする
    if "enough" in critique:
        return True
    elif "insufficient" in critique:
        return False
    else:
        raise ValueError("Critique does not contain a valid 0 or 1 for sufficiency check.")

def generate_response():
    """契約書の内容に基づいて応答を生成する関数"""
    payload = {
        "messages": [
            {"role": "user", "content": prompt + text}
        ],
        "temperature": 0.7,
        "max_tokens": args.max_tokens,
        "top_p": 0.95,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None
    }
    
    response = requests.post(base_url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    else:
        raise Exception(f"Error during generation: {response.status_code}")

# 生成と批評のループ
for iteration in range(args.max_iterations):
    print(f"Iteration {iteration+1}/{args.max_iterations}...")

    # 応答を生成
    generated_response = generate_response()
    print("Generated Response:")
    print(generated_response)

    # 批評を生成
    critique = critique_response(generated_response)
    print("Critique:")
    print(critique)

    # 批評が十分かどうかを判定
    if is_critique_sufficient(critique):
        print("The critique is sufficient. Ending loop.")
        break
    else:
        print("The critique is insufficient. Regenerating response...")

else:
    print("Reached maximum iterations. Ending loop.")