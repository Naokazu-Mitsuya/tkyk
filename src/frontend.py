import streamlit as st

if "results" not in st.session_state:
    st.session_state.results = []

# CSSファイルを読み込む関数
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 統合CSSを読み込む
load_css("/home/mitsuya/wsl-tkyk/front_copy/tkyk/src/pages/style.css")

summary_md = """
# Summary
## 個人情報
| 収集の有無 | 収集内容            | 共有の有無 | 共有の範囲               |
| ---------- | ------------------- | ---------- | ------------------------ |
| 有り       | 年齢、性別、閲覧履歴 | 有り       | ビジネス上のパートナー    |
"""
risky_statements = [
    {
        'id': 1,
        'category': 'データ管理',
        'tier': 1,
        'highlightText': 'ユーザーのデータは、法的要求がなくても法執行機関に提出される可能性があります。',
        'description': 'This is the explanation for term 1.',
        'originalText': 'ユーザーのデータは、法的要求がなくても法執行機関に提出される可能性があります。また、サービス利用中に生成されたデータは、任意の第三者にアクセス可能です。  ',
    },
    {
        'id': 2,
        'category': 'データ管理',
        'tier': 2,
        'highlightText': 'データ共有に関するユーザーのオプトアウト権は制限されています。',
        'description': 'This is the explanation for term 2.',
        'originalText': 'データ共有に関するユーザーのオプトアウト権は制限されています。',
    },
    {
        'id': 3,
        'category': 'データ管理',
        'tier': 3,
        'highlightText': 'サービスのパフォーマンス向上のためにデータが収集されることがあります。',
        'description': 'This is the explanation for term 3.',
        'originalText': 'サービスのパフォーマンス向上のためにデータが収集されることがあります。original',
    },
    {
        'id': 4,
        'category': 'データ管理',
        'tier': 4,
        'highlightText': 'サービス提供者は、データを定期的に更新・変更する権利を有します。',
        'description': 'This is the explanation for term 4.',
        'originalText': 'サービスのパフォーマンス向上のためにデータが収集されることがあります。original',
    },
    {
        'id': 3,
        'category': 'データ管理',
        'tier': 5,
        'highlightText': 'ユーザーが提供したフィードバックは、製品開発に使用される場合があります。',  
        'description': 'This is the explanation for term 5.',
        'originalText': 'ユーザーが提供したフィードバックは、製品開発に使用される場合があります。original',  
    },
]
def call_backend_api(terms_text, personal_info_text):
    return summary_md, risky_statements


st.title("契約書AI")
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
    response = call_backend_api(terms_text, personal_info_text)
    st.session_state.results.append(response)
    st.switch_page("pages/loading.py")