import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

MODEL_ID = "claude-sonnet-5-5"


def extract_text(response) -> str:
    """Extracts text while ignoring thinking/reasoning blocks."""
    for block in response.content:
        if getattr(block, "type", "") == "text":
            return block.text
    return ""


def run_researcher(topic: str) -> str:
    """Agent 1: Research Analyst - extracts core architectural insights."""
    print("🤖 Agent 1 (Researcher) is analyzing topic...")

    response = client.messages.create(
        model=MODEL_ID,
        max_tokens=1500,
        system="You are an expert technical researcher. Extract the 3 most crucial architectural pillars of the requested concept in clear bullet points. Avoid filler text.",
        messages=[
            {"role": "user", "content": f"Analyze and provide the 3 core pillars of: {topic}"}
        ]
    )
    return extract_text(response)


def run_writer(topic: str, research_data: str) -> str:
    """Agent 2: Technical Writer - synthesizes Agent 1's output."""
    print("🤖 Agent 2 (Writer) is drafting final summary...")

    response = client.messages.create(
        model=MODEL_ID,
        max_tokens=1500,
        system="You are an editor and technical writer. Synthesize raw research notes into an engaging, clear 2-paragraph overview suitable for beginners.",
        messages=[
            {
                "role": "user",
                "content": (
                    f"Topic: {topic}\n\n"
                    f"Researcher Notes:\n{research_data}\n\n"
                    "Turn these points into a clean, 2-paragraph summary."
                )
            }
        ]
    )
    return extract_text(response)


def main():
    topic = "Autonomous AI Agents and Multi-Agent Collaboration"

    print("\n" + "=" * 50)
    print("STARTING MULTI-AGENT PIPELINE")
    print("=" * 50 + "\n")

    # Step 1: Agent 1 does research
    research_notes = run_researcher(topic)
    print("\n--- [Agent 1 Output: Research Findings] ---")
    print(research_notes)

    print("\n" + "-" * 50 + "\n")

    # Step 2: Agent 2 receives Agent 1's work
    final_newsletter = run_writer(topic, research_notes)
    print("=== [Agent 2 Output: Final Deliverable] ===")
    print(final_newsletter)

    print("\n" + "=" * 50)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 50)


if __name__ == "__main__":
    main()