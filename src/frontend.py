import streamlit as st
#
## Frontend はsummary_md というmarkdownの表と、
#  risky_statements というリスクステートメントのリストを受け取る。これはjson???

# Frontendが受け取るデータの例
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
        'tier': 3,
        'highlightText': 'サービスのパフォーマンス向上のためにデータが収集されることがあります。',
        'description': 'This is the explanation for term 2.',
        'originalText': 'サービスのパフォーマンス向上のためにデータが収集されることがあります。original',
    },
    {
        'id': 3,
        'category': 'データ管理',
        'tier': 5,
        'highlightText': 'ユーザーが提供したフィードバックは、製品開発に使用される場合があります。',  
        'description': 'This is the explanation for term 3.',
        'originalText': 'ユーザーが提供したフィードバックは、製品開発に使用される場合があります。original',  
    },
]

# Tier-specific emojis and highlight colors
tier_emojis = {
    1: "⚫",  # Very high risk
    2: "🔴",  # High risk
    3: "🟠",  # Medium risk
    4: "🟡",  # Medium-low risk
    5: "🟢",  # Low risk
}

tier_colors = {
    1: "#FF4500",  # Orange red for very high risk
    2: "#FFA07A",  # Light coral for high risk
    3: "#FFD700",  # Gold for medium risk
    4: "#FFEC94",  # Light yellow for medium-low risk
    5: "#DFF2BF",  # Light green for low risk
}

def main():
    st.markdown(summary_md)
    st.markdown("## リスクステートメント")

    for statement in risky_statements:
        cols = st.columns([1, 4])  # Create two columns: one for the emoji, one for the text

        # Display emoji corresponding to the tier
        cols[0].markdown(f"<h1>{tier_emojis[statement['tier']]}</h1>", unsafe_allow_html=True)

        # Highlight the text based on tier and make it clickable to trigger the popover
        highlight_color = tier_colors[statement['tier']]

        # Render clickable highlighted text as the trigger for the popover
        html = f"""
        <span style="background-color:{highlight_color}; padding: 10px; cursor:pointer;" onclick="window.open('', 'popover')">
        {statement['highlightText']}
        </span>
        """
    
        # Display the text as clickable HTML
        cols[1].markdown(html, unsafe_allow_html=True)

    
        # Show a popover with description and original text when clicked
        with st.popover(f"Details for {statement['id']}"):
            st.write(f"**Description:** {statement['description']}")
            st.write(f"**Original Text:** {statement.get('originalText', 'No original text available.')}")
    # Loop through risky statements and render them

if __name__ == "__main__":
    main()
