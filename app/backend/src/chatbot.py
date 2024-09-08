import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain import hub
from langchain.schema import AIMessage, HumanMessage
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_core.runnables import RunnablePassthrough, RunnableSequence
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()


def initialize_vector_store() -> Chroma:
    """VectorStoreの初期化."""
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("DEPLOYMENT_EMBEDDINGS_NAME"),
        openai_api_version="2023-03-15-preview",
    )

    vector_store_path = "./resources/note.db"
    if Path(vector_store_path).exists():
        vector_store = Chroma(embedding_function=embeddings, persist_directory=vector_store_path)
    else:
        loader = TextLoader("./resources/note.txt")
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)

        vector_store = Chroma.from_documents(
            documents=splits, embedding=embeddings, persist_directory=vector_store_path
        )

    return vector_store


def initialize_retriever() -> VectorStoreRetriever:
    """Retrieverの初期化."""
    vector_store = initialize_vector_store()
    return vector_store.as_retriever().set_search_params(top_k=10)


def initialize_chain() -> RunnableSequence:
    """Langchainの初期化."""
    prompt = hub.pull("rlm/rag-prompt")
    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        openai_api_version="2023-03-15-preview",
        deployment_name=os.getenv("DEPLOYMENT_GPT_NAME"),
        openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        openai_api_type="azure",
    )
    retriever = initialize_retriever()
    chain = (
        {"context": retriever, "question": RunnablePassthrough()} | prompt | llm
    )
    return chain


def main() -> None:
    """ChatGPTを使ったチャットボットのメイン関数."""
    chain = initialize_chain()

    # ページの設定
    st.set_page_config(page_title="RAG ChatGPT")
    st.header("RAG ChatGPT")

    # チャット履歴の初期化
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # ユーザーの入力を監視
    if user_input := st.chat_input("聞きたいことを入力してね！"):
        st.session_state.messages.append(HumanMessage(content=user_input))
        with st.spinner("GPT is typing ..."):
            response = chain.invoke(user_input)
        st.session_state.messages.append(AIMessage(content=response.content))

    # チャット履歴の表示
    messages = st.session_state.get("messages", [])
    for message in messages:
        if isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.markdown(message.content)
        else:
            st.write(f"System message: {message.content}")


if __name__ == "__main__":
    main()