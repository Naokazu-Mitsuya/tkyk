# 法律文書のリスク評価システム (Guardian AI by team8 tech youth kingdom in ump_just_2024)

このプロジェクトは、法律文書のリスク評価を行うためのシステムです。Azure OpenAI（GPT-4）やCotomiを利用し、法律文書からの固有表現抽出、検索結果のRAG（Retrieval-Augmented Generation）、および度合い別のリスク事例集を基に、反射的評価（Reflection）を行います。

## 構成要素

- **Azure OpenAI**: 法律文書から固有表現を抽出し、リスク分析を行う。
- **Azure Bing Search**: ウェブ上の情報検索を行い、RAGのためにデータを収集する。
- **RAG (Retrieval-Augmented Generation)**: Bingからの検索結果を元に、GPT-4による文書生成を補強する技術。
- **Streamlit**: ユーザーインターフェースとして、Webベースのアプリケーションを提供する。
- **Cotomi**: Reflectionのためのリスク評価をサポートgit checkout mainする。

## システム図

システムの全体構成は以下の通りです（詳細は図をご参照ください）:

- **固有表現抽出**: Azure OpenAIを使用し、法律文書から重要な表現を抽出します。
- **ウェブ検索**: Bing Searchを使用して、関連する情報を収集し、リスク評価を補強します。
- **Reflection (反射的評価)**: Cotomiを使用して、法律文書のリスク評価を行います。
- **Streamlit サーバー**: ユーザーがインターフェースを介して文書をアップロードし、結果を確認します。

## 実行方法

### Dockerコンテナのビルド

以下のコマンドを使用して、Dockerイメージをビルドします。

```bash
docker build -t my-legal-risk-app .
```

### Dockerコンテナのスタート

```bash
docker run -it my-legal-risk-app
```
このコマンドで、Dockerコンテナを起動し、システムが実行されます。コンテナが起動すると、app.pyが実行され、リスク評価システムが動作します。

### APIキーの用意

```bash
cd /root
touch azure_gpt4o_key.txt bing_search_api_key.txt  cotomi_api_key.txt
```

### アプリケーションの実行
```bash
cd /mnt/app
python app.py
```
これにより、StreamlitベースのWebアプリケーションが起動され、ブラウザ上から法律文書のリスク評価を行うことができます。
