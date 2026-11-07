import os
import streamlit as st
from anthropic import Anthropic

st.set_page_config(page_title="Multi-Agent Pipeline", page_icon="🤖", layout="wide")

st.title("🤖 Multi-Agent Research & Writing Pipeline")
st.caption("Powered by direct Anthropic Claude API calls")

# Read API key from environment variable or sidebar input
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Anthropic API Key", type="password")

MODEL_ID = "claude-sonnet-5-5"


def extract_text(response) -> str:
    """Extracts text content while ignoring internal reasoning blocks."""
    for block in response.content:
        if getattr(block, "type", "") == "text":
            return block.text
    return ""


topic = st.text_input(
    "Enter a research topic:",
    value="Autonomous AI Agents and Multi-Agent Collaboration",
)

if st.button("Run Multi-Agent Pipeline", type="primary"):
    if not api_key:
        st.error("Please supply your ANTHROPIC_API_KEY.")
    else:
        client = Anthropic(api_key=api_key)

        # Agent 1: Researcher
        with st.status("Agent 1 (Researcher) is analyzing...", expanded=True) as status:
            res_response = client.messages.create(
                model=MODEL_ID,
                max_tokens=1500,
                system="You are an expert technical researcher. Extract the 3 most crucial architectural pillars of the requested concept in clear bullet points. Avoid filler text.",
                messages=[{"role": "user", "content": f"Analyze: {topic}"}],
            )
            research_notes = extract_text(res_response)
            status.update(label="Agent 1 (Researcher) finished!", state="complete")

        # Agent 2: Writer
        with st.status("Agent 2 (Writer) is drafting...", expanded=True) as status:
            writer_response = client.messages.create(
                model=MODEL_ID,
                max_tokens=1500,
                system="You are an editor and technical writer. Synthesize raw research notes into an engaging, clear 2-paragraph overview suitable for beginners.",
                messages=[
                    {
                        "role": "user",
                        "content": f"Topic: {topic}\n\nNotes:\n{research_notes}\n\nDraft a 2-paragraph guide.",
                    }
                ],
            )
            final_article = extract_text(writer_response)
            status.update(label="Agent 2 (Writer) finished!", state="complete")

        # Render outputs in side-by-side tabs
        tab1, tab2 = st.tabs(["Final Deliverable", "Raw Research Notes"])
        with tab1:
            st.markdown("### Published Overview")
            st.write(final_article)
        with tab2:
            st.markdown("### Background Insights")
            st.markdown(research_notes)