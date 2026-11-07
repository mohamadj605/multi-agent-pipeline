import os
import json
from ddgs import DDGS
from anthropic import Anthropic
from duckduckgo_search import DDGS

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("Missing ANTHROPIC_API_KEY. Run: $env:ANTHROPIC_API_KEY='your-key' in PowerShell.")

client = Anthropic(api_key=api_key)
MODEL_ID = "claude-sonnet-5-5"


def search_web(query: str) -> str:
    """Searches DuckDuckGo and returns top results."""
    print(f"  🔍 [Tool: Search] Running query: '{query}'")
    try:
        results = DDGS().text(query, max_results=3)
        return json.dumps(results)
    except Exception as e:
        return json.dumps({"error": str(e)})


def save_to_disk(filename: str, content: str) -> str:
    """Saves text content to a local file."""
    print(f"  💾 [Tool: Save] Writing deliverable to: {filename}")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Successfully saved to {filename}"


tools_schema = [
    {
        "name": "search_web",
        "description": "Searches the live web for recent information, facts, or technical documentation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query."}
            },
            "required": ["query"],
        },
    },
    {
        "name": "save_to_disk",
        "description": "Saves a generated report, code, or article to a local file on the computer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Name of the file, e.g., report.md"},
                "content": {"type": "string", "description": "Full text or markdown content to write"},
            },
            "required": ["filename", "content"],
        },
    },
]


def run_autonomous_agent(user_task: str):
    print(f"\n🚀 Task received: {user_task}\n")
    messages = [{"role": "user", "content": user_task}]

    while True:
        response = client.messages.create(
            model=MODEL_ID,
            max_tokens=2000,
            tools=tools_schema,
            messages=messages,
        )

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id

                    if tool_name == "search_web":
                        result = search_web(tool_input.get("query", ""))
                    elif tool_name == "save_to_disk":
                        result = save_to_disk(tool_input.get("filename", "output.txt"), tool_input.get("content", ""))
                    else:
                        result = "Unknown tool"

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": str(result),
                    })

            messages.append({"role": "user", "content": tool_results})
        else:
            for block in response.content:
                if getattr(block, "type", "") == "text":
                    print("\n✅ Final Report from Agent:\n")
                    print(block.text)
            break


if __name__ == "__main__":
    task = "Research the latest news on Anthropic Claude 3.5 Sonnet updates, summarize the key points, and save the result into 'claude_updates.md'."
    run_autonomous_agent(task)