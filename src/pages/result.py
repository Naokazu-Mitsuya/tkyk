import streamlit as st
# Tier-specific emojis and highlight colors
tier_emojis = {
    1: "⚫☠️",  # Very high risk
    2: "🔴🔥",  # High risk
    3: "🟠⚡",  # Medium risk
    4: "🟡⚠️",  # Medium-low risk
    5: "🟢✅",  # Low risk
}

tier_colors = {
    1: "#FF4500",  # Orange red for very high risk
    2: "#FFA07A",  # Light coral for high risk
    3: "#FFD700",  # Gold for medium risk
    4: "#FFEC94",  # Light yellow for medium-low risk
    5: "#DFF2BF",  # Light green for low risk
}

def main():
    if st.session_state.results is None or len(st.session_state.results) == 0:
        st.markdown("No results found.")
        st.session_state.results = []
        return
    summary_md, risky_statements = st.session_state.results[-1]
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
        with cols[1].popover(f"詳細"):
            st.write(f"**Description:** {statement['description']}")
            st.write(f"**Original Text:** {statement.get('originalText', 'No original text available.')}")
    # Loop through risky statements and render them

if __name__ == "__main__":
    main()
