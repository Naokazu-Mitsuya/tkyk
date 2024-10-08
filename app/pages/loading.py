import streamlit as st
import pandas as pd
from io import StringIO
import time
import random
import os

import sys
# sys.path.append("backend/src")  # `src` ディレクトリまでパスを追加
# 実際にAI model にAPIコールを投げる関数
from backend.src.call_api_by_func import call_func
def call_backend_api(terms_text, personal_info_text):
    if terms_text != "":
        response_terms = call_func(terms_text)
        return response_terms
    
    elif personal_info_text != "":
        response_personal_info = call_func(personal_info_text)
        return response_personal_info

    else:
        raise Exception("No text provided for analysis.")

# CSSファイルを読み込む関数
def load_css(file_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} が見つかりません。")
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 統合CSSを読み込む
load_css("style.css")

# ページ表示ロジック
st.markdown('<div class="loader"><div class="one"></div><div class="two"></div><div class="three"></div><div class="four"></div></div>', unsafe_allow_html=True)

messages = [
    "利用規約には、サービスの利用条件が細かく定められています。読まないことで、知らないうちに規約違反となるリスクも。",
    "プライバシーポリシーは、個人情報の取り扱いを定めたものです。読まないと、プライバシーが適切に保護されているか確認できません。",
    "利用規約には、損害賠償や免責事項など、重要な項目が含まれています。読まないと、トラブル時に不利益を被る可能性があります。",
    "利用規約には、サービスの利用制限やサービス内容の変更など、ユーザーの権利に関わる内容も含まれています。",
    "プライバシーポリシーには、データの共有や第三者提供に関する記載があります。読まないと、知らないうちに情報が共有されるリスクも。",
    "利用規約は、長文で読み飛ばしてしまいがちですが、重要な項目は必ず目を通しましょう。",
    "プライバシーポリシーは、個人情報を提供する上で、必ず読んでおくべき文書です。",
    "利用規約には、禁止事項や遵守事項など、サービスの利用に関するルールが詰まっています。",
    "利用規約やプライバシーポリシーは、サービス運営者とユーザー間の契約です。読まないと、契約内容を十分に理解できないまま利用することになります。",
    "利用規約には、退会手続きやアカウント削除に関する手続きも定められています。読まないと、退会時にトラブルになる可能性があります。",
    "プライバシーポリシーは、定期的に更新されることがあります。読まないと、最新のポリシー内容を把握できません。",
    "利用規約には、知的財産権や著作権に関する記載があります。読まないと、他者の権利を侵害してしまうリスクも。",
    "利用規約には、反社会的勢力排除に関する記載がある場合があります。読まないと、知らずに反社会的勢力と関わってしますリスクも。",
    "プライバシーポリシーには、個人情報に関する問い合わせ先も記載されています。読まないと、問い合わせ先を知らずに、トラブル時に困ってしまうかもしれません。",
    "利用規約やプライバシーポリシーは、サービスを利用する上でのルールブックです。必ず読んで、内容を理解してから利用しましょう。"
]


# ランダムに文章を選択
selected_message = random.choice(messages)

# 吹き出しの表示
st.markdown(
    """
    <style>
    .bubble {
        background: #f1f1f1;
        border-radius: 10px;
        padding: 10px; /* 吹き出しの内側余白を縮小 */
        max-width: 500px; /* 吹き出しの最大幅を調整 */
        font-size: 14px;
        position: absolute;
        bottom: -300px; /* 画面の下部に配置 */
        left: 50%; /* 画面の中央に水平配置 */
        transform: translateX(-50%); /* 横方向に中央揃え */
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* 軽い影を追加 */
    }
    .bubble::after {
        content: "";
        position: absolute;
        bottom: 100%;
        left: 10px;
        border-width: 10px;
        border-style: solid;
        border-color: transparent transparent #f1f1f1 transparent;
    }""" + f"""
    </style>
    <div class="bubble">
        {selected_message}
    </div>
    """,
    unsafe_allow_html=True
)
# Makes API calls here.
terms_text, personal_info_text = st.session_state["params"]
response = call_backend_api(terms_text, personal_info_text)
st.session_state.results.append(response)

    
file_path = os.path.join(os.path.dirname(__file__), "result.py")
# st.switch_page("./result.py")
st.switch_page(file_path)