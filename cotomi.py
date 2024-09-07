import streamlit as st
import pandas as pd
from io import StringIO

# Streamlitアプリ
def main():
    # ページの初期状態を設定
    if 'page' not in st.session_state:
        st.session_state.page = 'ページ1'

    st.title("2ページ構成のウェブサイト")

    # ページ設定
    if st.session_state.page == "ページ1":
        st.header("ページ1")
        st.write("以下のテキストボックスに情報を入力してください。")

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
            st.experimental_rerun()  # ページ遷移のために再実行

    elif st.session_state.page == "ページ2":
        # Markdown形式のテーブル
        markdown_table = """
        | 名前    | 年齢 | 職業      |
        |---------|------|-----------|
        | 佐藤太郎 | 25   | エンジニア |
        | 鈴木花子 | 30   | デザイナー |
        | 高橋一郎 | 28   | 教師      |
        """

        # Markdown テーブルから CSV 形式に変換
        csv_table = '\n'.join(
            row.strip().replace('|', ',').replace('  ', ' ').strip()
            for row in markdown_table.strip().split('\n')
        )
        csv_table = csv_table.replace(',\n', '\n')

        # StringIOを使ってCSVデータを読み込み
        data = StringIO(csv_table)
        # pandas DataFrame に変換
        df = pd.read_csv(data)

        # ハイライト関数
        def highlight_suzuki(s):
            return ['background-color: yellow' if '鈴木' in name else '' for name in s]

        st.header("ページ2")
        st.write("以下に要約結果が表示されます。")

        if 'terms_summary' in st.session_state and 'personal_info_summary' in st.session_state:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("利用規約の要約")
                # データフレームにハイライトスタイルを適用
                styled_df = df.style.apply(highlight_suzuki, subset=['名前'])
                st.dataframe(styled_df, width=600, height=300)

            with col2:
                st.subheader("個人情報関連の要約")
                st.markdown(markdown_table)  # 仮のデータとしてマークダウンテーブルを表示
        else:
            st.write("要約結果がありません。ページ1で情報を入力し、解析してください。")

if __name__ == "__main__":
    main()
