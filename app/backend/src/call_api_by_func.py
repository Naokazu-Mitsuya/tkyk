import os
import requests
import json
import concurrent.futures

# Set DEBUG flag
DEBUG = True  # Toggle this to False to disable print statements

# Function to print debug information when DEBUG is set to True
def debug_print(message):
    if DEBUG:
        print(message)

# Generate search query using GPT-4 (or Cotomi) for the search prompt
def generate_search_query_gpt4o(text, search_prompt):
    """Azure GPT-4 to generate search query based on contract text."""
    with open('/root/azure_gpt4o_key.txt') as f:
        key = f.read().strip()

    base_url = "https://aoai-ump-just-eastus.openai.azure.com/openai/deployments/aoai-gpt-4o/chat/completions?api-version=2023-05-15"
    headers = {'api-key': key, 'Content-Type': 'application/json'}
    
    prompt = search_prompt
    prompt += f"\n\n{text}"
    debug_print(prompt)

    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 50,
        "top_p": 0.95
    }

    response = requests.post(base_url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        result = response.json()
        search_query = result['choices'][0]['message']['content'].strip()
        debug_print(f"Generated Search Query: {search_query}")
        return search_query
    else:
        raise Exception(f"Error during search query generation: {response.status_code}")

# Bing search function
def search_bing(query):
    with open('/root/bing_search_api_key.txt') as f:
        subscription_key = f.read().strip()
    search_url = "https://api.bing.microsoft.com/v7.0/search"
    params = {"q": query, "count": 5, "responseFilter": "Webpages"}

    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()

    results = []
    for result in search_results['webPages']['value']:
        results.append({
            'name': result['name'],
            'url': result['url'],
            'snippet': result['snippet']
        })

    debug_print(f"Bing Search Results for '{query}': {json.dumps(results, indent=2)}")
    return results

# Final prompt generation function
def generate_final_prompt(contract_text, named_entities, web_results, first_prompt, rag_text):
    """Generates the final prompt for GPT-4 based on the named entities and web search results."""
    search_info = "\n## Web Search Results:\n"
    for result in web_results:
        search_info += f"**{result['name']}**\n\n[URL]({result['url']})\n\n{result['snippet']}\n\n"

    prompt = (
        f"# Extracted Named Entities\n"
        f"**Entities**: {named_entities}\n\n"
        f"## Search Results for Related Terms\n\n"
        f"{search_info}\n\n"
        "Based on the named entities and the related search results provided above, please analyze the potential contract risks."
    )

    # Add the RAG text to the prompt Tier sample
    rag = (
        f"# Tier Samples\n\n"
        f"{rag_text}\n\n"
        f"Based on the tier samples provided above, please analyze the potential contract risks."
    )


    prompt = f"{first_prompt}\n\n{contract_text}\n\n{rag}\n\n{prompt}"

    debug_print(f"Generated Final Prompt: {prompt}")
    return prompt

# GPT-4 from Azure to generate response
def generate_response_gpt4o(final_prompt):
    with open('/root/azure_gpt4o_key.txt') as f:
        key = f.read().strip()

    base_url = "https://aoai-ump-just-eastus.openai.azure.com/openai/deployments/aoai-gpt-4o/chat/completions?api-version=2023-05-15"
    headers = {'api-key': key, 'Content-Type': 'application/json'}
    payload = {
        "messages": [{"role": "user", "content": final_prompt}],
        "temperature": 0.7,
        "max_tokens": 1600,
        "top_p": 0.95
    }

    response = requests.post(base_url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        result = response.json()
        generated_response = result['choices'][0]['message']['content'].strip()
        debug_print(f"Generated Response: {generated_response}")
        return generated_response
    else:
        raise Exception(f"Error during generation: {response.status_code}")

# Critique response function for Cotomi
def critique_response_cotomi(response_content, review_prompt):
    """Cotomi critique function."""
    with open('/root/cotomi_api_key.txt') as f:
        key = f.read().strip()

    base_url = "https://api.cotomi.nec-cloud.com/oai-api/v1"
    headers = {'api-key': key, 'Content-Type': 'application/json'}

    critique_prompt = f"{review_prompt}\n\n{response_content}"
    payload = {
        "messages": [{"role": "user", "content": critique_prompt}],
        "temperature": 0.7,
        "max_tokens": 1600
    }

    response = requests.post(base_url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        result = response.json()
        critique = result['choices'][0]['message']['content'].strip()
        debug_print(f"Critique Response (Cotomi): {critique}")
        return critique
    else:
        raise Exception(f"Error during critique with Cotomi: {response.status_code}")

# Critique response function for GPT-4
def critique_response_gpt4o(response_content, review_prompt):
    """Azure GPT-4 critique function."""
    with open('/root/azure_gpt4o_key.txt') as f:
        key = f.read().strip()

    base_url = "https://aoai-ump-just-eastus.openai.azure.com/openai/deployments/aoai-gpt-4o/chat/completions?api-version=2023-05-15"
    headers = {'api-key': key, 'Content-Type': 'application/json'}

    critique_prompt = f"{review_prompt}\n\n{response_content}"
    payload = {
        "messages": [{"role": "user", "content": critique_prompt}],
        "temperature": 0.7,
        "max_tokens": 1600
    }

    critique_response = requests.post(base_url, headers=headers, data=json.dumps(payload))
    if critique_response.status_code == 200:
        result = critique_response.json()
        critique = result['choices'][0]['message']['content'].strip()
        debug_print(f"Critique Response (GPT-4): {critique}")
        return critique
    else:
        raise Exception(f"Error during critique with GPT-4: {critique_response.status_code}")

# Reflection loop function
def reflection_loop(final_prompt, review_prompt, engine, max_iterations=5):
    """Reflection loop to improve responses using GPT-4 or Cotomi."""
    for iteration in range(max_iterations):
        debug_print(f"Iteration {iteration+1}/{max_iterations}...")

        # First response generation
        generated_response = generate_response_gpt4o(final_prompt)
        if iteration == max_iterations - 1:
            debug_print("Final response generated.")
            break
        # Critique the response
        if engine == 'cotomi':
            critique = critique_response_cotomi(generated_response, review_prompt)
        else:
            critique = critique_response_gpt4o(generated_response, review_prompt)

        debug_print(f"Generated Response (Iteration {iteration+1}): {generated_response}")
        debug_print(f"Critique (Iteration {iteration+1}): {critique}")

        # Stop if the critique says it's sufficient
        if "insufficient" in critique:
            debug_print("The critique is insufficient. Regenerating response...")
        else:
            debug_print("The critique is sufficient. Ending the reflection loop.")
            break
    
    return generated_response

# Direct function call
def analyze_contract(contract_text, search_prompt, first_prompt, review_prompt, rag_text=None, engine='gpt4o', max_iterations=1):
    if not contract_text or not search_prompt:
        return {"error": "contract_text and search_prompt are required"}
    
    # Generate search query using GPT-4
    search_query = generate_search_query_gpt4o(contract_text, search_prompt)

    # Perform Bing search
    with concurrent.futures.ThreadPoolExecutor() as executor:
        web_search_future = executor.submit(search_bing, search_query)
        web_results = web_search_future.result()

    # Generate the final prompt
    final_prompt = generate_final_prompt(contract_text, search_query, web_results, first_prompt, rag_text)

    # Execute reflection loop (with GPT-4 or Cotomi based on selected engine)
    response = reflection_loop(final_prompt, review_prompt, engine, max_iterations)
    
    return {
        "analysis": response
    }

import re
import json

def extract_summary_and_risk_statements(analysis_text):
    # summaryの部分を抽出
    summary_match = re.search(r'"summary":\s*"([^"]*)"', analysis_text, re.DOTALL)
    summary = summary_match.group(1).strip() if summary_match else ""

    # risky_statementの部分を抽出
    risky_statements = []
    risky_statement_matches = re.findall(r'\{(.*?)\}', analysis_text, re.DOTALL)
    
    for match in risky_statement_matches:
        # 各リスクステートメントの詳細情報を抽出
        id_match = re.search(r'"id":\s*(\d+)', match)
        category_match = re.search(r'"category":\s*"([^"]*)"', match)
        tier_match = re.search(r'"tier":\s*(\d+)', match)
        highlight_text_match = re.search(r'"highlightText":\s*"([^"]*)"', match)
        description_match = re.search(r'"description":\s*"([^"]*)"', match)
        original_text_match = re.search(r'"originalText":\s*"([^"]*)"', match)

        # リスクステートメントの各フィールドを辞書にして追加
        risky_statements.append({
            "id": int(id_match.group(1)) if id_match else None,
            "category": category_match.group(1) if category_match else "",
            "tier": int(tier_match.group(1)) if tier_match else None,
            "highlightText": highlight_text_match.group(1) if highlight_text_match else "",
            "description": description_match.group(1) if description_match else "",
            "originalText": original_text_match.group(1) if original_text_match else ""
        })

    # risky_statementsをJSON文字列に変換
    risky_statements_json = json.dumps(risky_statements, ensure_ascii=False, indent=2)

    return summary, risky_statements_json


# Sample usage
# 新しい `call_func` 関数
def call_func(contract_text, search_prompt_path = '/mnt/app/backend/input_sample/search_prompt.txt',
              first_prompt_path = '/mnt/app/backend/input_sample/first_prompt.txt', 
              review_prompt_path = '/mnt/app/backend/input_sample/review_prompt.txt', 
              rag_path = '/mnt/app/backend/input_sample/tier_examples.txt', engine = 'cotomi'):
    with open(rag_path, 'r', encoding='utf-8') as f:
        rag_text = f.read()

    # Load contract text
    # with open(file_path, 'r', encoding='utf-8') as f:
    #     contract_text = f.read()

    # Load search prompt text
    with open(search_prompt_path, 'r', encoding='utf-8') as f:
        search_prompt_text = f.read()

    # Load review prompt text
    with open(review_prompt_path, 'r', encoding='utf-8') as f:
        review_prompt_text = f.read()

    # Load first prompt text
    with open(first_prompt_path, 'r', encoding='utf-8') as f:
        first_prompt_text = f.read().strip()

    # `analyze_contract` 関数を呼び出し、サーバーレスで直接処理する
    result = analyze_contract(
        contract_text=contract_text, 
        search_prompt=search_prompt_text, 
        first_prompt=first_prompt_text, 
        review_prompt=review_prompt_text, 
        rag_text=rag_text, 
        engine=engine
    )

    # 結果を出力
    print(result)
    result = extract_summary_and_risk_statements(result['analysis'])
    return result


# メイン関数
if __name__ == "__main__":
    # Set the file paths and parameters
    rag_path = '/mnt/app/backend/input_sample/tier_examples.txt'
    file_path = '/mnt/app/backend/input_sample/bereal.txt'
    with open(file_path, 'r', encoding='utf-8') as f:
        contract_text = f.read()
    
    search_prompt_path = '/mnt/app/backend/input_sample/search_prompt.txt'
    first_prompt_path = '/mnt/app/backend/input_sample/first_prompt.txt'
    review_prompt_path = '/mnt/app/backend/input_sample/review_prompt.txt'
    engine = 'gpt4o'  # or 'kotomi' depending on the model you use

    # サーバーレス関数を呼び出し
    response = call_func(contract_text, search_prompt_path, first_prompt_path, review_prompt_path, rag_path, engine)
    print(response[0])
    print("======================")
    print(response[1])