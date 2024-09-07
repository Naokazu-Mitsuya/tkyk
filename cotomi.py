import streamlit as st
import pandas as pd
from io import StringIO

# カスタムCSSを定義
highlight_css = """
    <style>
     mark {
     background-color: yellow;
     color: black;  /* 文字色を黒に */
     }
    </style>
    """
button_css = """
<style>
  div.stButton {
    display: flex;
    justify-content: center;          /* 水平中央揃え */
    align-items: center;              /* 垂直中央揃え */
    cursor: pointer;                  /* ポインタカーソルにする */
    padding: 60px 20px;
  }
  div.stButton  > button:first-child {
    font-weight: bold;                /* 文字：太字 */
    background: #ddd;                 /* 背景色：薄いグレー */
    border: none;                     /* ボーダーを削除 */
    padding: 10px 20px;               /* パディングを設定 */
    border-radius: 5px;               /* 角を丸くする */
  }
</style>
"""

table_css = """
<style>
    /* 表を画面の横幅いっぱいにする */
table {
  width: 100%;
  border-collapse: collapse;
}

/* カラム幅を指定する */
th:nth-child(1), td:nth-child(1) {
  width: 30%; /* 1列目の幅を30%に設定 */
}

th:nth-child(2), td:nth-child(2) {
  width: 40%; /* 2列目の幅を40%に設定 */
}

th:nth-child(3), td:nth-child(3) {
  width: 30%; /* 3列目の幅を30%に設定 */
}

/* 表のスタイル設定 */
th, td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

th {
  background-color: #f2f2f2;
  color: #333;
}

tr:nth-child(even) {
  background-color: #f9f9f9;
}

tr:hover {
  background-color: #ddd;
}
</style>
"""

st.markdown(highlight_css, unsafe_allow_html=True)
st.markdown(button_css, unsafe_allow_html=True)
st.markdown(table_css, unsafe_allow_html=True)

# Streamlitアプリ
def main():
    # ページの初期状態を設定
    if 'page' not in st.session_state:
        st.session_state.page = 'ページ1'

    st.title("契約書AI")

    # ページ設定
    if st.session_state.page == "ページ1":
        st.header("契約書情報入力")
        st.write("以下のテキストボックスに契約書情報を入力してください。")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("利用規約")
            terms_text = st.text_area("利用規約テキスト", height=200)

        with col2:
            st.subheader("個人情報関連")
            personal_info_text = st.text_area("個人情報関連テキスト", height=200)

        if st.button("解析"):
            # ページ2に遷移
            st.session_state.page = 'ページ2'
            st.rerun()
        
            
    elif st.session_state.page == "ページ2":
        # 与えられたマークダウン形式のデータ
        markdown_table_data = """
            | 名前    | 年齢 | ランク      |
            |---------|------|-----------|
            | 佐藤太郎 | 25   | ランク1 |
            | 鈴木花子 | 30   | ランク2 |
            | 高橋一郎 | 28   | ランク3   |
        """

        # ランクに基づいて行の名前列をハイライトする関数
        def highlight_name_column(data, rank_to_highlight):
            lines = data.split("\n")
            header = lines[0]
            separator = lines[1]
    
            highlighted_lines = [header, separator]
    
            for line in lines[2:]:
                if "|" in line:
                    columns = line.split("|")
                    if rank_to_highlight in line:
                        # 名前列をハイライト
                        columns[1] = f"<mark>{columns[1].strip()}</mark>"
                    highlighted_lines.append("|".join(columns))
            return "\n".join(highlighted_lines)

        # "ランク2"が含まれる行の名前列をハイライト
        highlighted_markdown_table = highlight_name_column(markdown_table_data, "ランク2")

        # マークダウン形式のテーブルを表示
        st.markdown(highlighted_markdown_table, unsafe_allow_html=True)

# アプリケーションの実行
if __name__ == "__main__":
    main()
