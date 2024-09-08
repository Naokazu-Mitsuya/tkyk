import requests
import json

def call_analyze_contract_api(file_path, search_prompt_path, first_prompt_path, review_prompt_path, rag_path, engine, api_url):
    with open(rag_path, 'r', encoding='utf-8') as f:
        rag_text = f.read()
    # Load contract text
    with open(file_path, 'r', encoding='utf-8') as f:
        contract_text = f.read()

    # Load search prompt text
    with open(search_prompt_path, 'r', encoding='utf-8') as f:
        search_prompt_text = f.read()

    # Load review prompt text
    with open(review_prompt_path, 'r', encoding='utf-8') as f:
        review_prompt_text = f.read()

    with open(first_prompt_path, 'r', encoding='utf-8') as f:
        first_prompt_text = f.read().strip()

    # Prepare the data to be sent in the API request
    data = {
        "rag_text": rag_text,
        "contract_text": contract_text,
        "search_prompt": search_prompt_text,  # The search prompt content goes here
        "first_prompt": first_prompt_text,       # The first prompt content
        "review_prompt": review_prompt_text,       # The review prompt content
        "engine": engine,                          # Include engine choice, either 'gpt4o' or 'kotomi'
        "max_iterations": 5                        # Set max_iterations, modify if needed
    }

    # Send POST request to the Flask API
    response = requests.post(api_url, json=data)

    # Check response and output result
    if response.status_code == 200:
        result = response.json()
        print("API Response:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # Set the file paths and API endpoint
    rag_path = '/mnt/app/backend/input_sample/tier_examples.txt'
    file_path = '/mnt/app/backend/input_sample/bereal.txt'
    search_prompt_path = '/mnt/app/backend/input_sample/search_prompt.txt'
    first_prompt_path = '/mnt/app/backend/input_sample/first_prompt.txt'
    review_prompt_path = '/mnt/app/backend/input_sample/review_prompt.txt'
    engine = 'kotomi'  # or 'kotomi' if using a different model
    api_url = 'http://127.0.0.1:5000/analyze_contract'  # Your Flask server's endpoint

    # Call the API
    call_analyze_contract_api(file_path, search_prompt_path, first_prompt_path, review_prompt_path, rag_path, engine, api_url)