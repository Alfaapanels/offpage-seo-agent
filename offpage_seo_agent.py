#!/usr/bin/env python3
"""
Daily Off-Page SEO Agent for alfaapanels.com
Finds and acts on relevant backlink opportunities every day.
"""

import anthropic
from datetime import datetime
from pathlib import Path

client = anthropic.Anthropic()

DOMAIN = "alfaapanels.com"
BRAND = "Alfa Panels"
NICHE = "solar panels, insulated building panels, structural panels, construction materials, energy solutions"
COMPETITORS = ["kingspanpanels.com", "metlspan.com", "centria.com", "nucorskyline.com"]
KEYWORDS = ["solar panels", "building panels", "insulated panels", "SIP panels", "construction panels", "alfa panels"]

REPORTS_DIR = Path("daily_reports")
REPORTS_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def analyze_backlink_quality(backlink_url: str, anchor_text: str) -> str:
    signals = []
    generic = ["click here", "website", "here", "link", "read more", "this site"]
    if anchor_text.lower() in generic:
        signals.append("Warning: Generic anchor text – low SEO value")
    else:
        signals.append(f"Good: Descriptive anchor text – '{anchor_text}'")

    toxic = ["spam", "casino", "viagra", "porn", "xxx", "pills", "gambling"]
    if any(w in backlink_url.lower() for w in toxic):
        signals.append("TOXIC LINK – disavow strongly recommended")
    else:
        signals.append("Domain appears clean")

    if any(s in backlink_url for s in [".edu", ".gov", ".org"]):
        signals.append("High-authority domain – excellent link")
    elif any(s in backlink_url for s in ["solar", "panel", "energy", "construct", "build"]):
        signals.append("Niche-relevant domain – strong contextual link")

    return "\n".join(signals)


def categorize_brand_mention(mention_text: str) -> str:
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive = ["great", "best", "excellent", "recommend", "love", "amazing", "quality", "reliable", "trusted"]
    negative = ["bad", "worst", "avoid", "scam", "terrible", "poor", "unreliable", "fraud"]
    pos = sum(1 for w in positive if w in mention_text.lower())
    neg = sum(1 for w in negative if w in mention_text.lower())
    sentiment = "Positive" if pos > neg else "Negative" if neg > pos else "Neutral"
    kind = "Linked mention" if has_link else "Unlinked mention (link building opportunity!)"
    action = "Monitor & track" if has_link else "Reach out to request link addition"
    return f"Type: {kind}\nSentiment: {sentiment}\nAction: {action}"


def score_link_prospect(page_url: str, page_title: str, page_snippet: str) -> str:
    score = 0
    reasons = []
    niche_words = [w.strip() for w in NICHE.split(",")]
    content = (page_title + " " + page_snippet).lower()

    relevance = sum(1 for w in niche_words if w.lower() in content)
    if relevance >= 2:
        score += 40
        reasons.append("High niche relevance (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate relevance (+20)")
    else:
        reasons.append("Low relevance (+0)")

    high_value = ["resource", "guide", "tools", "blog", "list", "best", "top", "directory", "links"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value):
        score += 30
        reasons.append("Resource/guide/directory page (+30)")

    if any(s in page_url for s in [".edu", ".gov", ".org"]):
        score += 30
        reasons.append("High-authority domain (.edu/.gov/.org) (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")

    priority = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    reason_lines = "\n".join(f"  - {r}" for r in reasons)
    return f"Score: {score}/100 [{priority} PRIORITY]\nURL: {page_url}\nBreakdown:\n{reason_lines}"


def generate_outreach_email(
    prospect_name: str,
    prospect_site: str,
    page_topic: str,
    link_type: str,
    your_content_url: str,
) -> str:
    url = your_content_url if your_content_url.startswith("http") else f"https://alfaapanels.com/{your_content_url}"
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I was reading your page about {page_topic} on {prospect_site} and spotted a broken link "
            f"that might frustrate your readers.\n\n"
            f"We have a comprehensive resource at {url} that covers this topic in depth and would make "
            f"a perfect replacement — no strings attached.\n\n"
            f"Would you consider swapping it in?\n\n"
            f"Best regards,\n[Your Name]\nAlfa Panels | alfaapanels.com"
        ),
        "guest_post": (
            f"Subject: Guest post idea for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I love your content about {page_topic} on {prospect_site} — really actionable stuff.\n\n"
            f"I'd love to contribute a guest post on [specific angle relevant to their audience]. "
            f"I write for Alfa Panels (alfaapanels.com), where we cover panels, construction, and "
            f"sustainable building.\n\n"
            f"Would you be open to a collaboration? Happy to send a few headline ideas first.\n\n"
            f"Best regards,\n[Your Name]\nAlfa Panels | alfaapanels.com"
        ),
        "resource": (
            f"Subject: Suggestion for your {page_topic} resource page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {page_topic} is one of the best I've found — very thorough!\n\n"
            f"I created a guide at {url} that I think would be a valuable addition for your readers. "
            f"It covers [specific benefit].\n\n"
            f"Would you be open to taking a look?\n\n"
            f"Best regards,\n[Your Name]\nAlfa Panels | alfaapanels.com"
        ),
        "mention": (
            f"Subject: Thank you for mentioning Alfa Panels!\n\n"
            f"Hi {prospect_name},\n\n"
            f"I noticed you mentioned Alfa Panels in your article about {page_topic} on {prospect_site} — thank you!\n\n"
            f"Would you consider adding a direct link to {url}? It would help your readers find us easily "
            f"and give them access to [specific resource].\n\n"
            f"Thanks so much!\n[Your Name]\nAlfa Panels | alfaapanels.com"
        ),
        "directory": (
            f"Subject: Directory listing request – Alfa Panels\n\n"
            f"Hi {prospect_name},\n\n"
            f"I'd like to submit Alfa Panels (alfaapanels.com) to your {page_topic} directory.\n\n"
            f"We manufacture high-quality solar panels, structural insulated panels, and building panels "
            f"for residential and commercial projects.\n\n"
            f"Could you point me to your submission process?\n\n"
            f"Best regards,\n[Your Name]\nAlfa Panels | alfaapanels.com"
        ),
    }
    return templates.get(link_type, templates["resource"])


def identify_link_gap(competitor_domain: str, linking_page_topic: str) -> str:
    return (
        f"LINK GAP OPPORTUNITY\n"
        f"Competitor with this link: {competitor_domain}\n"
        f"Linking page topic: {linking_page_topic}\n"
        f"Your domain: alfaapanels.com\n\n"
        f"3-step action plan:\n"
        f"1. Find the exact content on {competitor_domain} that earned this link\n"
        f"2. Create a more comprehensive, up-to-date resource on '{linking_page_topic}' for alfaapanels.com\n"
        f"3. Pitch the linking site your superior resource as a replacement or addition"
    )


# ---------------------------------------------------------------------------
# Tool schemas and dispatch
# ---------------------------------------------------------------------------

TOOL_SCHEMAS = [
    {
        "name": "analyze_backlink_quality",
        "description": "Evaluate the quality and relevance of a backlink pointing to alfaapanels.com.",
        "input_schema": {
            "type": "object",
            "properties": {
                "backlink_url": {"type": "string", "description": "URL of the site linking to alfaapanels.com"},
                "anchor_text": {"type": "string", "description": "Anchor text of the link"},
            },
            "required": ["backlink_url", "anchor_text"],
        },
    },
    {
        "name": "categorize_brand_mention",
        "description": "Categorize an Alfa Panels brand mention as linked/unlinked and assess its sentiment.",
        "input_schema": {
            "type": "object",
            "properties": {
                "mention_text": {"type": "string", "description": "Text snippet containing the brand mention"},
            },
            "required": ["mention_text"],
        },
    },
    {
        "name": "score_link_prospect",
        "description": "Score a potential link building prospect page for relevance and authority.",
        "input_schema": {
            "type": "object",
            "properties": {
                "page_url": {"type": "string", "description": "URL of the prospect page"},
                "page_title": {"type": "string", "description": "Title of the page"},
                "page_snippet": {"type": "string", "description": "Short content snippet from the page"},
            },
            "required": ["page_url", "page_title", "page_snippet"],
        },
    },
    {
        "name": "generate_outreach_email",
        "description": "Generate a personalized outreach email for a link building opportunity.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prospect_name": {"type": "string", "description": "Name of the website owner or editor"},
                "prospect_site": {"type": "string", "description": "Their website name or URL"},
                "page_topic": {"type": "string", "description": "Topic of the page where you want a link"},
                "link_type": {
                    "type": "string",
                    "enum": ["broken_link", "guest_post", "resource", "mention", "directory"],
                    "description": "Type of link building opportunity",
                },
                "your_content_url": {
                    "type": "string",
                    "description": "URL path or full URL of your content to be linked",
                },
            },
            "required": ["prospect_name", "prospect_site", "page_topic", "link_type", "your_content_url"],
        },
    },
    {
        "name": "identify_link_gap",
        "description": "Identify a link gap opportunity where a competitor has a backlink that alfaapanels.com lacks.",
        "input_schema": {
            "type": "object",
            "properties": {
                "competitor_domain": {"type": "string", "description": "The competitor's domain"},
                "linking_page_topic": {"type": "string", "description": "Topic of the page linking to the competitor"},
            },
            "required": ["competitor_domain", "linking_page_topic"],
        },
    },
    {"type": "web_search_20260209", "name": "web_search"},
    {"type": "web_fetch_20260209", "name": "web_fetch"},
]

TOOL_HANDLERS = {
    "analyze_backlink_quality": lambda a: analyze_backlink_quality(a["backlink_url"], a["anchor_text"]),
    "categorize_brand_mention": lambda a: categorize_brand_mention(a["mention_text"]),
    "score_link_prospect": lambda a: score_link_prospect(a["page_url"], a["page_title"], a["page_snippet"]),
    "generate_outreach_email": lambda a: generate_outreach_email(
        a["prospect_name"], a["prospect_site"], a["page_topic"], a["link_type"], a["your_content_url"]
    ),
    "identify_link_gap": lambda a: identify_link_gap(a["competitor_domain"], a["linking_page_topic"]),
}


def _execute_tool(name: str, args: dict) -> str:
    handler = TOOL_HANDLERS.get(name)
    if handler:
        try:
            return handler(args)
        except Exception as e:
            return f"Tool error: {e}"
    return f"Unknown tool: {name}"


# ---------------------------------------------------------------------------
# Agentic loop
# ---------------------------------------------------------------------------

def _run_agent_loop(system: str, user_prompt: str) -> list[str]:
    messages = [{"role": "user", "content": user_prompt}]
    text_outputs: list[str] = []

    while True:
        response = client.beta.messages.create(
            model="claude-opus-4-6",
            max_tokens=16000,
            system=system,
            tools=TOOL_SCHEMAS,
            messages=messages,
            betas=["web-search-2025-03-05"],
        )

        messages.append({"role": "assistant", "content": response.content})

        for block in response.content:
            if getattr(block, "type", None) == "text":
                print(block.text)
                text_outputs.append(block.text)

        if response.stop_reason == "end_turn":
            break

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if getattr(block, "type", None) == "tool_use":
                    if block.name in TOOL_HANDLERS:
                        result = _execute_tool(block.name, block.input)
                        preview = result[:120].replace("\n", " ")
                        print(f"  [Tool: {block.name}] {preview}…")
                    else:
                        result = "Handled by API"
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            if tool_results:
                messages.append({"role": "user", "content": tool_results})
        else:
            break

    return text_outputs


# ---------------------------------------------------------------------------
# Daily backlink session
# ---------------------------------------------------------------------------

def run_daily_backlink_agent() -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{'=' * 60}")
    print(f"Daily Backlink Builder – alfaapanels.com")
    print(f"Date: {today}")
    print(f"{'=' * 60}\n")

    system = (
        f"You are an expert off-page SEO strategist running a daily backlink building session for "
        f"alfaapanels.com – a manufacturer of high-quality solar panels, structural insulated panels (SIPs), "
        f"and building panels. Today's date: {today}.\n\n"
        f"Your job: find REAL, current backlink opportunities using web_search and web_fetch, then use the "
        f"specialist tools to score, analyse, and produce ready-to-send outreach emails. Be specific – "
        f"include actual URLs and domain names. Quality over quantity."
    )

    prompt = f"""Build relevant backlinks for alfaapanels.com today. Work through every task below:

---

**TASK 1 – Brand Mention Audit**
Search: "Alfa Panels" -site:alfaapanels.com
For every unlinked mention found, use categorize_brand_mention then generate_outreach_email (type: mention).
Target: 3 outreach emails ready to send.

---

**TASK 2 – Niche Directory Submissions**
Search: site:solar-directory OR site:greenenergy-directory "submit listing" panels
Also search: "solar panels supplier directory" submit
Find 5 relevant directories. Score each with score_link_prospect.
Generate a directory outreach email for the top 3.

---

**TASK 3 – Competitor Backlink Gap Analysis**
For each competitor below, find sites that link to them but not to alfaapanels.com:
Competitors: {', '.join(COMPETITORS)}
Search: link:kingspanpanels.com OR link:metlspan.com panels resource
Use identify_link_gap for the 3 best opportunities.

---

**TASK 4 – Guest Post Outreach**
Search: "write for us" "solar panels" OR "construction panels" OR "building materials"
Search: "guest post" "structural panels" OR "insulated panels"
Score the top 5 prospects with score_link_prospect.
Generate a guest_post outreach email for each HIGH or MEDIUM priority prospect.

---

**TASK 5 – Resource Page Link Building**
Search: intitle:"resources" OR intitle:"useful links" "solar panels" OR "building panels" site:.org OR site:.edu
Find 5 resource pages. Score them. Generate resource outreach emails for top 3.

---

**TASK 6 – Broken Link Opportunities**
Search: "solar panels resource page" OR "construction panels resources" broken links
Fetch any resource pages found and check for dead or outdated links we could replace.
Use analyze_backlink_quality on any new links for alfaapanels.com discovered.

---

**TASK 7 – Q&A & Forum Participation**
Search: site:quora.com "best solar panels" OR "which construction panels"
Search: site:reddit.com/r/solar OR site:reddit.com/r/DIY panels question
Identify the top 3 questions where linking to alfaapanels.com adds value.
Write a short, helpful answer for each (include how/where to naturally place the link).

---

**TASK 8 – Daily Action Summary**
Produce a clean, prioritised report with:
1. Top 5 IMMEDIATE actions (paste-ready email + target URL for each)
2. Top 5 MEDIUM-TERM opportunities (1–2 weeks)
3. Estimated backlinks that could be built this week if outreach is sent today
4. KPIs to track next session"""

    parts = _run_agent_loop(system, prompt)

    report_path = REPORTS_DIR / f"backlinks_{today}.md"
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report – alfaapanels.com\n")
        f.write(f"**Date:** {today}\n\n")
        f.write("\n\n---\n\n".join(parts))

    print(f"\nReport saved → {report_path}")
    return str(report_path)


if __name__ == "__main__":
    run_daily_backlink_agent()
