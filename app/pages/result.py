import json
import streamlit as st

# Tier-specific emojis and highlight colors
tier_emojis = {
    1: "️☠️☠️️️☠☠️☠️️️️️️",  # Very high risk
    2: "🔥🔥🔥🔥",  # High risk
    3: "⚡⚡⚡",  # Medium risk
    4: "⚠️⚠️", # Medium-low risk
    5: "✅",  # Low risk
}

tier_colors = {
    1: "#FF4500",  # Orange red for very high risk
    2: "#FFA07A",  # Light coral for high risk
    3: "#FFD700",  # Gold for medium risk
    4: "#FFEC94",  # Light yellow for medium-low risk
    5: "#DFF2BF",  # Light green for low risk
}

def main():
    # If no results are found in the session state
    if st.session_state.get('results') is None or len(st.session_state['results']) == 0:
        st.markdown("No results found.")
        st.session_state['results'] = []
        return
    
    # Unpack the results
    summary_md, risky_statements_json = st.session_state['results'][-1]

    # risky_statementsがJSON文字列の場合、辞書リストに変換する
    if isinstance(risky_statements_json, str):
        try:
            risky_statements = json.loads(risky_statements_json)  # JSON文字列を辞書に変換
        except json.JSONDecodeError:
            st.error("リスクステートメントのデコードに失敗しました。")
            return
    else:
        risky_statements = risky_statements_json  # すでに辞書リストならそのまま使う

    # Summaryを表示
    summary_md_cleaned = summary_md.replace("  ", "") 
    st.markdown(summary_md_cleaned)
    st.markdown("## リスクステートメント")

    # Loop through each risk statement and display them
    for statement in risky_statements:
        # Create two columns: one for the emoji and one for the text
        cols = st.columns([1, 4])  

        # Display the emoji corresponding to the risk tier
        cols[0].markdown(f"<h3>{tier_emojis[statement['tier']]}</h3>", unsafe_allow_html=True)

        # Set the background color based on the risk tier
        highlight_color = tier_colors[statement['tier']]
        html = f"""
        <span style="background-color:{highlight_color}; padding: 10px;">
        {statement['highlightText']}
        </span>
        """
        # Display the highlighted text
        cols[1].markdown(html, unsafe_allow_html=True)

        # Use expander to show the description and original text when clicked
        with cols[1].expander("詳細を表示"):
            st.write(f"**Description:** {statement['description']}")
            st.write(f"**Original Text:** {statement.get('originalText', 'No original text available.')}")

if __name__ == "__main__":
    main()