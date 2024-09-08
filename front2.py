import streamlit as st
import pandas as pd
from io import StringIO
import time

# カスタムCSSを定義
import streamlit as st

# CSSファイルを読み込む関数
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 統合CSSを読み込む
load_css("/home/mitsuya/wsl-tkyk/front/style.css")


# ページの初期状態を設定
if 'page' not in st.session_state:
    st.session_state.page = 'ページ1'
if 'loading' not in st.session_state:
    st.session_state.loading = False

# ローディングアニメーションを表示してからページ遷移する関数
def start_loading_and_transition():
    st.session_state.loading = True
    st.rerun()


# ページ表示ロジック
if st.session_state.loading:
    # ローディングアニメーションを表示
    st.markdown('<div class="loader"><div class="one"></div><div class="two"></div><div class="three"></div><div class="four"></div></div>', unsafe_allow_html=True)
        # 擬似的な処理の遅延
    time.sleep(3)
    
    # ページ2に遷移
    st.session_state.page = 'ページ2'
    st.session_state.loading = False
    st.rerun()

else:
    if st.session_state.page == 'ページ1':
        # ページ1の内容
        st.header("契約書情報入力")
        st.write("以下のテキストボックスに契約書情報を入力してください。")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("利用規約")
            terms_text = st.text_area("利用規約テキスト", height=200)

        with col2:
            st.subheader("個人情報関連")
            personal_info_text = st.text_area("個人情報関連テキスト", height=200)

        # 解析ボタンを押すとローディング画面を表示し、その後ページ2に遷移
        if st.button("解析"):
            start_loading_and_transition()

    elif st.session_state.page == 'ページ2':
        # ページ2の内容
        st.header("解析結果")

        # 結果の表示（この部分は任意にカスタマイズ可能）
        st.write("解析が完了しました！以下に結果を表示します。")
