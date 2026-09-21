"""Daily backlink building agent for alfaapanels.com"""
import anthropic
import json
import os
from datetime import date

client = anthropic.Anthropic()

DOMAIN = "alfaapanels.com"
BRAND = "Alfa Panels"
NICHE = "aluminum composite panels, architectural cladding, facade systems, building materials"
COMPETITORS = [
    "alpolic.com",
    "reynobond.com",
    "alucobond.com",
    "dibond.com",
    "alucobest.com",
]

TOOLS = [
    {
        "name": "score_link_prospect",
        "description": "Score a potential link building prospect for relevance and authority.",
        "input_schema": {
            "type": "object",
            "properties": {
                "page_url": {"type": "string", "description": "URL of prospect page"},
                "page_title": {"type": "string", "description": "Title of the page"},
                "relevance_score": {"type": "integer", "description": "0-100 relevance score"},
                "authority_estimate": {"type": "string", "enum": ["low", "medium", "high", "very_high"]},
                "link_type": {"type": "string", "enum": ["guest_post", "resource_page", "broken_link", "directory", "forum", "blog_comment", "niche_mention"]},
                "outreach_priority": {"type": "string", "enum": ["high", "medium", "low"]},
            },
            "required": ["page_url", "page_title", "relevance_score", "authority_estimate", "link_type", "outreach_priority"],
        },
    },
    {
        "name": "generate_outreach_email",
        "description": "Generate a personalized outreach email for a link building prospect.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prospect_url": {"type": "string"},
                "contact_name": {"type": "string"},
                "link_type": {"type": "string"},
                "subject": {"type": "string"},
                "email_body": {"type": "string"},
            },
            "required": ["prospect_url", "link_type", "subject", "email_body"],
        },
    },
    {
        "name": "record_backlink_opportunity",
        "description": "Record a confirmed backlink opportunity with full details.",
        "input_schema": {
            "type": "object",
            "properties": {
                "opportunity_type": {"type": "string"},
                "target_url": {"type": "string"},
                "description": {"type": "string"},
                "action_required": {"type": "string"},
                "estimated_impact": {"type": "string", "enum": ["low", "medium", "high"]},
            },
            "required": ["opportunity_type", "target_url", "description", "action_required", "estimated_impact"],
        },
    },
]


def run_tool(name: str, inputs: dict) -> str:
    if name == "score_link_prospect":
        return json.dumps({
            "scored": True,
            "url": inputs["page_url"],
            "score": inputs["relevance_score"],
            "priority": inputs["outreach_priority"],
        })
    elif name == "generate_outreach_email":
        return json.dumps({"generated": True, "prospect": inputs["prospect_url"]})
    elif name == "record_backlink_opportunity":
        return json.dumps({"recorded": True, "type": inputs["opportunity_type"]})
    return json.dumps({"status": "ok"})


def run_agent() -> dict:
    today = date.today().isoformat()
    messages = [
        {
            "role": "user",
            "content": f"""You are an expert off-page SEO strategist specializing in link building for B2B industrial and construction material companies.

Today's date: {today}
Target website: {DOMAIN}
Brand: {BRAND}
Niche: {NICHE}
Main competitors: {', '.join(COMPETITORS)}

Your task: Generate TODAY's daily backlink building plan. Find 8-12 specific, real, actionable backlink opportunities.

Consider these link types for construction/building materials:
1. Architecture and construction industry directories (AIA, CSI, Arcat, Sweets, SpecifiedBy)
2. Building products databases (Arcat.com, BIMobject, NBS Source)
3. Architecture blogs and publications (ArchDaily, Dezeen, Architizer)
4. Construction trade magazines and sites (Construction Dive, ENR, Building Design+Construction)
5. Interior design resource pages (Houzz, Architectural Digest, Contract)
6. Green building / sustainability sites (LEED, USGBC, Green Building Advisor)
7. Aluminum industry associations (The Aluminum Association, European Aluminium)
8. DIY / contractor forums (ContractorTalk, GarageJournal)
9. Guest post opportunities on construction/architecture blogs
10. YouTube channel descriptions and comments on architectural facade videos
11. Reddit communities (r/architecture, r/construction, r/DIY)
12. LinkedIn articles and groups for architects and contractors

For each opportunity, use the score_link_prospect tool, then generate_outreach_email where applicable, then record_backlink_opportunity.

After identifying all opportunities, provide a comprehensive daily action plan with specific outreach targets."""
        }
    ]

    prospects = []
    outreach_emails = []
    opportunities = []
    final_report_text = ""

    for _ in range(20):  # max iterations
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=8000,
            tools=TOOLS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        # Collect text
        for block in response.content:
            if block.type == "text" and block.text.strip():
                final_report_text += block.text + "\n\n"

        if response.stop_reason == "end_turn":
            break

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = run_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
                    if block.name == "score_link_prospect":
                        prospects.append(block.input)
                    elif block.name == "generate_outreach_email":
                        outreach_emails.append(block.input)
                    elif block.name == "record_backlink_opportunity":
                        opportunities.append(block.input)

            if tool_results:
                messages.append({"role": "user", "content": tool_results})
        else:
            break

    return {
        "date": today,
        "domain": DOMAIN,
        "prospects": prospects,
        "outreach_emails": outreach_emails,
        "opportunities": opportunities,
        "report": final_report_text,
    }


def save_report(data: dict) -> str:
    today = data["date"]
    filename = f"backlink_report_{today}.md"
    filepath = os.path.join(os.path.dirname(__file__), "reports", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    lines = [
        f"# Daily Backlink Report: {data['domain']}",
        f"**Date:** {today}",
        "",
        "## Summary",
        f"- Prospects scored: {len(data['prospects'])}",
        f"- Outreach emails generated: {len(data['outreach_emails'])}",
        f"- Opportunities recorded: {len(data['opportunities'])}",
        "",
    ]

    if data["prospects"]:
        lines.append("## Scored Prospects")
        for p in data["prospects"]:
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(p.get("outreach_priority", ""), "•")
            lines.append(f"### {priority_emoji} {p.get('page_title', 'Unknown')}")
            lines.append(f"- **URL:** {p.get('page_url', '')}")
            lines.append(f"- **Relevance:** {p.get('relevance_score', 0)}/100")
            lines.append(f"- **Authority:** {p.get('authority_estimate', '')}")
            lines.append(f"- **Type:** {p.get('link_type', '')}")
            lines.append(f"- **Priority:** {p.get('outreach_priority', '')}")
            lines.append("")

    if data["outreach_emails"]:
        lines.append("## Outreach Emails")
        for e in data["outreach_emails"]:
            lines.append(f"### To: {e.get('prospect_url', '')}")
            lines.append(f"**Subject:** {e.get('subject', '')}")
            lines.append("")
            lines.append(e.get("email_body", ""))
            lines.append("")

    if data["opportunities"]:
        lines.append("## Recorded Opportunities")
        for o in data["opportunities"]:
            impact_emoji = {"high": "⭐⭐⭐", "medium": "⭐⭐", "low": "⭐"}.get(o.get("estimated_impact", ""), "")
            lines.append(f"### {impact_emoji} {o.get('opportunity_type', '')}")
            lines.append(f"- **Target:** {o.get('target_url', '')}")
            lines.append(f"- **Description:** {o.get('description', '')}")
            lines.append(f"- **Action:** {o.get('action_required', '')}")
            lines.append("")

    if data["report"]:
        lines.append("## Agent Analysis & Action Plan")
        lines.append("")
        lines.append(data["report"])

    content = "\n".join(lines)
    with open(filepath, "w") as f:
        f.write(content)

    print(f"Report saved: {filepath}")
    return filepath


if __name__ == "__main__":
    print(f"Running daily backlink agent for {DOMAIN}...")
    data = run_agent()
    report_path = save_report(data)
    print(f"\nCompleted. Prospects: {len(data['prospects'])}, Emails: {len(data['outreach_emails'])}, Opportunities: {len(data['opportunities'])}")
