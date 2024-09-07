import os
import glob
from pathlib import Path
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import uuid

# 環境変数の読み込み
load_dotenv()

def parse_xml_file(file_path: str) -> str:
    """XMLファイルを解析し、法律テキストを抽出して返す"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # 法律のタイトルを取得
        law_title = root.find('.//LawTitle').text

        # 法律本文（条文、段落、文章）を取得
        articles = root.findall('.//Article')
        law_text = law_title + "\n"

        for article in articles:
            article_title = article.find('.//ArticleTitle').text
            paragraphs = article.findall('.//Paragraph')

            law_text += article_title + "\n"

            for paragraph in paragraphs:
                sentences = paragraph.findall('.//Sentence')
                for sentence in sentences:
                    law_text += sentence.text + "\n"

        return law_text.strip()

    except Exception as e:
        print(f"Failed to parse {file_path}: {e}")
        return ""


def get_all_law_texts_from_directory(directory: str) -> str:
    """ディレクトリ内のすべてのXMLファイルを読み込み、法律テキストを結合して返す"""
    law_texts = ""
    xml_files = glob.glob(os.path.join(directory, '**/*.xml'), recursive=True)
    
    for xml_file in xml_files:
        law_text = parse_xml_file(xml_file)
        if law_text:
            law_texts += law_text + "\n\n"

    return law_texts.strip()


def initialize_vector_store(text: str) -> None:
    """法律のテキストをベクトル化し、Chromaベクトルストアに保存"""
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("DEPLOYMENT_EMBEDDINGS_NAME"),
        openai_api_version="2023-03-15-preview",
    )

    vector_store_path = "./resources/law_vector_store.db"

    # 既存のベクトルストアがある場合は処理をスキップ
    if Path(vector_store_path).exists():
        print(f"{vector_store_path} already exists. Skipping vector store creation.")
        return

    # テキストをチャンクに分割
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_text(text)

    if not splits:
        raise ValueError("Text splitting resulted in an empty list. Ensure the input text is not empty.")

    # 各テキストチャンクに一意のIDを割り当てる
    ids = [str(uuid.uuid4()) for _ in splits]

    # ベクトルストアに保存
    vector_store = Chroma.from_documents(
        documents=splits, embedding=embeddings, persist_directory=vector_store_path, ids=ids
    )

    print(f"Vector store created and saved to {vector_store_path}.")


def main() -> None:
    """法律データをXMLファイルから取得し、ベクトルストアに保存する"""
    law_directory = './resources/'  # XMLファイルが含まれているディレクトリ
    print(f"Loading law texts from {law_directory}...")
    law_texts = get_all_law_texts_from_directory(law_directory)

    if not law_texts.strip():
        raise ValueError("No valid law texts were found. Ensure the XML files are properly structured.")

    print("Initializing vector store...")
    initialize_vector_store(law_texts)
    print("Vector store initialization completed.")


if __name__ == "__main__":
    main()