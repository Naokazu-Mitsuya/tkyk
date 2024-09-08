from langchain.schema import Document  # 追加
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
    """XMLファイルを解析し、法律テキストを抽出して返す。要素がない場合は空文字列を使用。"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # 法律のタイトルを取得（存在しない場合は空文字列）
        law_title_element = root.find('.//LawTitle')
        law_title = law_title_element.text if law_title_element is not None else "No Title"

        # 法律の制定文（EnactStatement）
        enact_statement_element = root.find('.//EnactStatement')
        enact_statement = enact_statement_element.text if enact_statement_element is not None else "No Enact Statement"

        # 法律本文（MainProvision）
        articles = root.findall('.//MainProvision/Paragraph')
        law_text = (law_title or "") + "\n" + (enact_statement or "") + "\n"

        for article in articles:
            # 各段落の文章を取得
            sentences = article.findall('.//Sentence')
            for sentence in sentences:
                sentence_text = sentence.text if sentence.text is not None else ""
                law_text += sentence_text + "\n"

        # 附則（SupplProvision）も抽出
        suppl_provisions = root.findall('.//SupplProvision')
        for suppl_provision in suppl_provisions:
            suppl_label_element = suppl_provision.find('.//SupplProvisionLabel')
            suppl_label = suppl_label_element.text if suppl_label_element is not None else "No SupplProvision Label"
            law_text += (suppl_label or "") + "\n"

            paragraphs = suppl_provision.findall('.//Paragraph')
            for paragraph in paragraphs:
                sentences = paragraph.findall('.//Sentence')
                for sentence in sentences:
                    sentence_text = sentence.text if sentence.text is not None else ""
                    law_text += sentence_text + "\n"

        return law_text.strip()

    except ET.ParseError:
        print(f"Error: Failed to parse {file_path}, invalid XML format.")
        return ""
    except Exception as e:
        print(f"Failed to parse {file_path}: {e}")
        return ""


def get_all_law_texts_from_directory(directory: str) -> list:
    """ディレクトリ内のすべてのXMLファイルを読み込み、法律テキストを結合して返す"""
    documents = []
    xml_files = glob.glob(os.path.join(directory, '**/*.xml'), recursive=True)
    
    for xml_file in xml_files:
        law_text = parse_xml_file(xml_file)
        if law_text:
            # Documentオブジェクトに変換してリストに追加
            documents.append(Document(page_content=law_text, metadata={"source": xml_file}))

    return documents


def initialize_vector_store(documents: list, batch_size: int = 100) -> None:
    """法律のテキストをバッチごとにベクトル化し、Chromaベクトルストアに保存"""
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("DEPLOYMENT_EMBEDDINGS_NAME"),
        openai_api_version="2023-03-15-preview",
    )

    vector_store_path = "./resources/law_vector_store.db"

    # 既存のベクトルストアがある場合は処理をスキップ
    if Path(vector_store_path).exists():
        print(f"{vector_store_path} already exists. Skipping vector store creation.")
        return

    # バッチ処理でベクトル化を行う
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]

        # テキストをチャンクに分割
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(batch)

        if not splits:
            raise ValueError("Text splitting resulted in an empty list. Ensure the input text is not empty.")

        # 各テキストチャンクに一意のIDを割り当てる
        ids = [str(uuid.uuid4()) for _ in splits]

        # ベクトルストアに保存
        vector_store = Chroma.from_documents(
            documents=splits, embedding=embeddings, persist_directory=vector_store_path, ids=ids
        )

        print(f"Processed batch {i // batch_size + 1}/{(len(documents) + batch_size - 1) // batch_size}")

    print(f"Vector store created and saved to {vector_store_path}.")


def main() -> None:
    """法律データをXMLファイルから取得し、ベクトルストアに保存する"""
    law_directory = './resources/'  # XMLファイルが含まれているディレクトリ
    print(f"Loading law texts from {law_directory}...")
    documents = get_all_law_texts_from_directory(law_directory)

    if not documents:
        raise ValueError("No valid law texts were found. Ensure the XML files are properly structured.")

    print("Initializing vector store...")
    initialize_vector_store(documents, batch_size=100)
    print("Vector store initialization completed.")


if __name__ == "__main__":
    main()