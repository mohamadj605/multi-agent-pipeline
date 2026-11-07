import os
import anthropic

# Initialize the client. This automatically looks for the ANTHROPIC_API_KEY environment variable.
client = anthropic.Anthropic()

def run_agent(agent_role, task_prompt, output_filename):
    print(f"[*] Spinning up {agent_role}...")
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2500,
            system=f"You are a {agent_role}.",
            messages=[
                {"role": "user", "content": task_prompt}
            ]
        )
        # Extract the text content from Claude's response
        output = response.content[0].text
        
        with open(output_filename, "w", encoding="utf-8") as file:
            file.write(output)
        print(f"[+] Success: {agent_role} output saved to {output_filename}\n")
    except Exception as e:
        print(f"[-] Error running {agent_role}: {e}\n")

# --- PROMPTS ---

bom_prompt = """
Write a local Python script that acts as a Bill of Materials (BOM) and Quoting Calculator for "Apex Laser Designs".
It must prompt the user for:
1. Material Type (White Oak, Walnut, Matte Black Acrylic, Clear Acrylic)
2. Width and Height (in inches)

It should calculate:
- Total square inches.
- Material cost (Oak = $0.15/sq in, Walnut = $0.18/sq in, Acrylic = $0.10/sq in).
- Estimated laser time (2 mins per sq inch at $2.00/minute).
- A 40% B2B markup on the final total.
Output a clean, formatted command-line summary. Provide ONLY the raw Python code, no markdown formatting or explanations.
"""

seo_prompt = """
Write the complete profile copy for my Google Business Profile for "Apex Laser Designs" (a B2B architectural laser fabrication shop in Toronto).
Provide:
1. A 750-character Business Description focusing on corporate signage, custom fabrication, and B2B executive awards. Use local SEO keywords for the GTA.
2. A list of 5 primary "Services" to add to the profile, including a 2-sentence SEO-optimized description for each.
3. Three ideas for the first Google Business "Update" posts to signal to the algorithm that we take commercial clients.
"""

email_prompt = """
Write a professional, concise email autoresponder for B2B clients who submit a project intake form on the Apex Laser Designs website.
The tone must be premium, industrial, and highly responsive.
Acknowledge receipt of their dimensions and vector files, state that our engineering team is reviewing the specs to calculate a Bill of Materials (BOM), and establish that they will receive a formal quote within 24 hours. No generic corporate fluff.
"""

# --- EXECUTION ---

if __name__ == "__main__":
    print("Initializing Apex Laser Designs Multi-Agent Pipeline via Claude...\n")
    
    # Agent 1: The Manufacturing Engineer (Writes the BOM Python script)
    run_agent("Senior Python Developer and Manufacturing Engineer", bom_prompt, "bom_calculator.py")
    
    # Agent 2: The Local SEO Expert (Writes the Google Business Profile copy)
    run_agent("Local SEO Expert for Service Area Businesses", seo_prompt, "Google_SEO_Profile.txt")
    
    # Agent 3: The B2B Account Manager (Writes the automated email response)
    run_agent("B2B Account Manager", email_prompt, "Email_Autoresponder.txt")
    
    print("Pipeline execution complete. Have a good time with your friends.")