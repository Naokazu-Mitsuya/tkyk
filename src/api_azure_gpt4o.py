import os
import requests
import json
import argparse
from openai import OpenAI  # kotomi用のOpenAIモジュール

# 引数の設定
parser = argparse.ArgumentParser(description="Analyze contract risks using either Azure GPT-4 or Cotomi models.")
parser.add_argument('--file_path', type=str, required=True, help="Path to the text file containing contract data.")
parser.add_argument('--max_tokens', type=int, default=800, help="Maximum number of tokens to generate.")
parser.add_argument('--prompt_path', type=str, default=None, help="Path to the text file containing the prompt.")
parser.add_argument('--max_iterations', type=int, default=5, help="Maximum number of reflection iterations.")
parser.add_argument('--review_prompt', type=str, default=None, help="Path to the text file containing the review prompt.")
parser.add_argument('--engine', type=str, required=True, choices=['gpt4o', 'kotomi'], help="Specify the engine to use for inference.")
args = parser.parse_args()

# 共通部分の契約書データとプロンプトの読み込み
with open(args.file_path) as f:
    text = f.read().strip()

with open(args.prompt_path) as f:
    prompt = f.read().strip()

with open(args.review_prompt) as f:
    review_prompt = f.read().strip()

def critique_response_gpt4o(response_content):
    """Azure GPT-4で生成された応答の批評を行う関数"""
    with open('/root/azure_gpt4o_key.txt') as f:
        key = f.read().strip()

    base_url = "https://aoai-ump-just-eastus.openai.azure.com/openai/deployments/aoai-gpt-4o/chat/completions?api-version=2023-05-15"
    headers = {
        'api-key': key,
        'Content-Type': 'application/json'
    }
    
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

def critique_response_kotomi(response_content):
    """Cotomiで生成された応答の批評を行う関数"""
    with open('/root/cotomi_api_key.txt') as f:
        key = f.read().strip()

    client = OpenAI(
        api_key=key, 
        base_url="https://api.cotomi.nec-cloud.com/oai-api/v1"
    )

    critique_prompt = f"{review_prompt}\n\n{response_content}"
    response = client.chat.completions.create(
        model="cotomi-core-pro-v1.0-awq", 
        messages=[{"role": "user", "content": critique_prompt}],
        temperature=0.7,
        max_tokens=300,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )

    return response.choices[0].message.content.strip()

def generate_response_gpt4o():
    """Azure GPT-4で契約書の内容に基づいて応答を生成する関数"""
    with open('/root/azure_gpt4o_key.txt') as f:
        key = f.read().strip()

    base_url = "https://aoai-ump-just-eastus.openai.azure.com/openai/deployments/aoai-gpt-4o/chat/completions?api-version=2023-05-15"
    headers = {
        'api-key': key,
        'Content-Type': 'application/json'
    }

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

def generate_response_kotomi():
    """Cotomiで契約書の内容に基づいて応答を生成する関数"""
    with open('/root/cotomi_api_key.txt') as f:
        key = f.read().strip()

    client = OpenAI(
        api_key=key, 
        base_url="https://api.cotomi.nec-cloud.com/oai-api/v1"
    )

    response = client.chat.completions.create(
        model="cotomi-core-pro-v1.0-awq",
        messages=[{"role": "user", "content": prompt + text}],
        temperature=0.7,
        max_tokens=args.max_tokens,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )

    return response.choices[0].message.content.strip()

def call_gpt4o_reflection():
    """指定されたエンジンを使用して反映ループを実行する関数"""
    for iteration in range(args.max_iterations):
        print(f"Iteration {iteration+1}/{args.max_iterations}...")
        
        generated_response = generate_response_gpt4o()
        if args.engine == 'gpt4o':
            critique = critique_response_gpt4o(generated_response)
        elif args.engine == 'kotomi':
            critique = critique_response_kotomi(generated_response)

        print("Generated Response:")
        print(generated_response)

        if iteration == args.max_iterations - 1:
            print("Reached maximum iterations. Ending loop.")
            break

        print("Critique:")
        print(critique)

        # 批評が十分かどうかを判定
        if "enough" in critique:
            print("The critique is sufficient. Ending loop.")
            break
        else:
            print("The critique is insufficient. Regenerating response...")

    else:
        print("Reached maximum iterations. Ending loop.")
    return generated_response

# 実行
call_gpt4o_reflection()