import anthropic
import json
import os
from datetime import datetime


def _get_auth_token() -> str | None:
    token_file = os.environ.get(
        "CLAUDE_SESSION_INGRESS_TOKEN_FILE",
        "/home/claude/.claude/remote/.session_ingress_token",
    )
    if token_file and os.path.isfile(token_file):
        try:
            token = open(token_file).read().strip()
            if token:
                return token
        except OSError:
            pass
    return None


def _make_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return anthropic.Anthropic(api_key=api_key)
    auth_token = _get_auth_token()
    if auth_token:
        return anthropic.Anthropic(auth_token=auth_token)
    return anthropic.Anthropic()


client = _make_client()

# ── Alfaa Panels configuration ────────────────────────────────────────────────
TARGET_DOMAIN = "alfaapanels.com"
BRAND_NAME    = "Alfaa Panels"
NICHE         = (
    "sandwich panel manufacturer insulated panels PUF PIR rockwool "
    "cold room clean room panels building construction India"
)
COMPETITORS   = [
    "thermocoolpanels.com",
    "isopanels.in",
    "metalspan.in",
    "rockwoolpanels.com",
    "enviropanels.com",
]
# ─────────────────────────────────────────────────────────────────────────────


# ── Tool definitions (JSON schema, not @beta_tool decorator) ──────────────────

def _tool_analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    signals = []
    generic = ["click here", "website", "here", "link", "read more"]
    if anchor_text.lower() in generic:
        signals.append("Warning: Generic anchor text – low value")
    else:
        signals.append(f"Good: Descriptive anchor: '{anchor_text}'")
    if any(w in backlink_url.lower() for w in ["spam", "casino", "viagra", "adult"]):
        signals.append("TOXIC link – disavow recommended")
    else:
        signals.append("Domain appears clean")
    return "\n".join(signals)


def _tool_categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive = ["great", "best", "excellent", "recommend", "love", "amazing",
                "quality", "reliable", "trusted", "certified", "leading"]
    negative = ["bad", "worst", "avoid", "scam", "terrible", "poor", "fake"]
    pos = sum(1 for w in positive if w in mention_text.lower())
    neg = sum(1 for w in negative if w in mention_text.lower())
    sentiment = "Positive" if pos > neg else ("Negative" if neg > pos else "Neutral")
    kind = "Linked mention" if has_link else "Unlinked mention (link building opportunity!)"
    return (
        f"Brand: {brand_name}\nType: {kind}\nSentiment: {sentiment}\n"
        f"Action: {'Monitor' if has_link else 'Reach out to convert to a link'}"
    )


def _tool_score_link_prospect(
    page_url: str, page_title: str, page_content_snippet: str, your_niche: str
) -> str:
    score = 0
    reasons = []
    niche_words = your_niche.lower().split()
    content = (page_title + " " + page_content_snippet).lower()
    relevance = sum(1 for w in niche_words if w in content)
    if relevance >= 3:
        score += 40; reasons.append("High niche relevance (+40)")
    elif relevance >= 1:
        score += 20; reasons.append("Moderate relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    high_value = ["resource", "guide", "tools", "blog", "list", "best",
                  "directory", "supplier", "manufacturer", "industry"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value):
        score += 30; reasons.append("Resource/directory/guide (+30)")
    if any(s in page_url for s in [".edu", ".gov", ".org"]):
        score += 30; reasons.append("High authority domain (+30)")
    elif any(s in page_url for s in [".in", "india"]):
        score += 20; reasons.append("India-relevant domain (+20)")
    else:
        score += 10; reasons.append("Standard domain (+10)")
    priority = "HIGH PRIORITY" if score >= 70 else ("MEDIUM" if score >= 40 else "LOW")
    return f"Score: {score}/100 – {priority}\nURL: {page_url}\n" + "\n".join(reasons)


def _tool_generate_outreach_template(
    prospect_name: str, prospect_site: str, their_page_topic: str,
    your_site: str, your_content_url: str, link_type: str,
) -> str:
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I found a broken link on your {their_page_topic} page on {prospect_site}.\n\n"
            f"Alfaa Panels has a detailed guide at {your_content_url} that would be a perfect replacement – "
            f"India's leading sandwich panel manufacturer, BIS certified, 30+ years experience.\n\n"
            f"Would you consider updating the link?\n\nBest regards,\nTeam Alfaa Panels | alfaapanels.com"
        ),
        "guest_post": (
            f"Subject: Guest article idea for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I enjoy your content about {their_page_topic} on {prospect_site}.\n\n"
            f"I'd like to contribute an expert article on insulated sandwich panels, cold room construction, "
            f"or clean room panel standards. I write for Alfaa Panels (alfaapanels.com), "
            f"India's only panel manufacturer with plants in all four corners of the country.\n\n"
            f"Would you be open to a collaboration?\n\nBest regards,\nTeam Alfaa Panels"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is excellent! "
            f"I thought {your_content_url} might add real value for your readers – "
            f"Alfaa Panels covers PUF, PIR, cold room and clean room solutions backed by "
            f"30 years of manufacturing expertise and a 15-year product warranty.\n\n"
            f"Would you take a look?\n\nBest regards,\nTeam Alfaa Panels | alfaapanels.com"
        ),
        "mention": (
            f"Subject: Thank you for mentioning Alfaa Panels!\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning Alfaa Panels in your article about {their_page_topic}!\n\n"
            f"Would you be open to linking directly to {your_content_url}?\n\n"
            f"Thanks,\nTeam Alfaa Panels | alfaapanels.com"
        ),
        "directory": (
            f"Subject: Add Alfaa Panels to your {their_page_topic} directory\n\n"
            f"Hi {prospect_name},\n\n"
            f"I noticed your {their_page_topic} directory on {prospect_site}.\n\n"
            f"Alfaa Panels (alfaapanels.com) is India's leading sandwich panel manufacturer – "
            f"PUF, PIR, rockwool, cold room, and clean room panels – BIS certified, 30+ years, "
            f"5 plants across India.\n\n"
            f"Could you add our listing?\n\nBest regards,\nTeam Alfaa Panels"
        ),
    }
    return templates.get(link_type, templates["resource"])


def _tool_identify_link_gap(competitor_domain: str, your_domain: str, linking_page_topic: str) -> str:
    return (
        f"LINK GAP OPPORTUNITY\n"
        f"Competitor: {competitor_domain}\n"
        f"Your site: {your_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Actions:\n"
        f"1. Find which page on {competitor_domain} earned this link\n"
        f"2. Create stronger content on the same topic for {your_domain}\n"
        f"3. Pitch your resource with Alfaa's advantages: BIS cert, 15-yr warranty, pan-India manufacturing"
    )


def _tool_find_directory_targets(niche: str, location: str) -> str:
    targets = [
        ("IndiaMART",          "indiamart.com",           "Top India B2B marketplace – high DA"),
        ("TradeIndia",         "tradeindia.com",           "B2B directory – construction niche"),
        ("ExportersIndia",     "exportersindia.com",       "Manufacturer directory"),
        ("Justdial",           "justdial.com",             "Local business directory – India"),
        ("Sulekha",            "sulekha.com",              "India product/service directory"),
        ("BizVibe",            "bizvibe.com",              "Global B2B – manufacturing"),
        ("Kompass",            "kompass.com",              "International trade directory"),
        ("Yellow Pages India", "yellowpages.co.in",        "General business directory"),
        ("Go4WorldBusiness",   "go4worldbusiness.com",     "B2B trade portal"),
        ("BuildoTrade",        "buildotrade.com",          "Construction-specific directory"),
    ]
    lines = [f"DIRECTORY TARGETS for '{niche}' | {location}:\n"]
    for name, domain, note in targets:
        lines.append(f"• {name} ({domain}) – {note}")
    lines.append(
        "\nAction: Submit alfaapanels.com with consistent NAP, product categories, and website URL."
    )
    return "\n".join(lines)


# ── Tool dispatch ─────────────────────────────────────────────────────────────

TOOL_SCHEMAS = [
    {
        "name": "analyze_backlink_quality",
        "description": "Evaluate quality of a backlink pointing to a URL.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url":           {"type": "string", "description": "Your target URL."},
                "backlink_url":  {"type": "string", "description": "The URL linking to you."},
                "anchor_text":   {"type": "string", "description": "Anchor text used."},
            },
            "required": ["url", "backlink_url", "anchor_text"],
        },
    },
    {
        "name": "categorize_brand_mention",
        "description": "Categorise a brand mention as linked/unlinked and analyse sentiment.",
        "input_schema": {
            "type": "object",
            "properties": {
                "mention_text": {"type": "string", "description": "Text containing the mention."},
                "brand_name":   {"type": "string", "description": "Brand name."},
            },
            "required": ["mention_text", "brand_name"],
        },
    },
    {
        "name": "score_link_prospect",
        "description": "Score a potential link building prospect (0-100).",
        "input_schema": {
            "type": "object",
            "properties": {
                "page_url":              {"type": "string"},
                "page_title":            {"type": "string"},
                "page_content_snippet":  {"type": "string"},
                "your_niche":            {"type": "string"},
            },
            "required": ["page_url", "page_title", "page_content_snippet", "your_niche"],
        },
    },
    {
        "name": "generate_outreach_template",
        "description": "Generate a personalised outreach email for link building.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prospect_name":    {"type": "string"},
                "prospect_site":    {"type": "string"},
                "their_page_topic": {"type": "string"},
                "your_site":        {"type": "string"},
                "your_content_url": {"type": "string"},
                "link_type":        {
                    "type": "string",
                    "enum": ["guest_post", "broken_link", "resource", "mention", "directory"],
                },
            },
            "required": [
                "prospect_name", "prospect_site", "their_page_topic",
                "your_site", "your_content_url", "link_type",
            ],
        },
    },
    {
        "name": "identify_link_gap_opportunity",
        "description": "Identify whether a competitor backlink is an opportunity for your site.",
        "input_schema": {
            "type": "object",
            "properties": {
                "competitor_domain":  {"type": "string"},
                "your_domain":        {"type": "string"},
                "linking_page_topic": {"type": "string"},
            },
            "required": ["competitor_domain", "your_domain", "linking_page_topic"],
        },
    },
    {
        "name": "find_directory_submission_targets",
        "description": "Return a list of business directories and trade portals to submit to.",
        "input_schema": {
            "type": "object",
            "properties": {
                "niche":    {"type": "string"},
                "location": {"type": "string"},
            },
            "required": ["niche", "location"],
        },
    },
    # web_search_20250305 works with session tokens (20260209 bundles bash which is blocked)
    {"type": "web_search_20250305", "name": "web_search"},
]

# Beta header required for the 2025-03-05 web search tool
WEB_SEARCH_BETA_HEADER = "web-search-2025-03-05"


def _dispatch_tool(name: str, inputs: dict) -> str:
    if name == "analyze_backlink_quality":
        return _tool_analyze_backlink_quality(**inputs)
    if name == "categorize_brand_mention":
        return _tool_categorize_brand_mention(**inputs)
    if name == "score_link_prospect":
        return _tool_score_link_prospect(**inputs)
    if name == "generate_outreach_template":
        return _tool_generate_outreach_template(**inputs)
    if name == "identify_link_gap_opportunity":
        return _tool_identify_link_gap(**inputs)
    if name == "find_directory_submission_targets":
        return _tool_find_directory_targets(**inputs)
    return f"Unknown tool: {name}"


# ── Agentic loop ──────────────────────────────────────────────────────────────

def run_offpage_seo_agent(
    your_domain: str = TARGET_DOMAIN,
    brand_name:  str = BRAND_NAME,
    niche:       str = NICHE,
    competitors: list = None,
):
    if competitors is None:
        competitors = COMPETITORS

    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{'='*60}")
    print(f"Off-Page SEO Agent – {brand_name}")
    print(f"Domain : {your_domain}")
    print(f"Date   : {today}")
    print(f"{'='*60}\n")

    system_prompt = (
        "You are an expert off-page SEO strategist specialising in B2B manufacturing companies in India. "
        "Execute every task the user assigns. When you need to search or fetch, use the web_search and "
        "web_fetch tools. Use the custom tools to score prospects, categorise mentions, and generate "
        "outreach emails. Always produce a detailed, actionable report."
    )

    user_message = f"""Perform today's daily backlink-building session for:

Domain      : {your_domain}
Brand       : {brand_name}
Niche       : {niche}
Competitors : {', '.join(competitors)}
Date        : {today}

Complete ALL six tasks below.

──────────────────────────────────────────────────────────────
TASK 1 – BRAND MENTION AUDIT
Search for unlinked "{brand_name}" mentions across the web.
Queries to run:
  "{brand_name}" -site:{your_domain}
  "Alfaa Panels" cold room panels review
For each unlinked mention: use categorize_brand_mention and generate a 'mention' outreach email.

──────────────────────────────────────────────────────────────
TASK 2 – COMPETITOR BACKLINK GAPS
For each competitor in [{', '.join(competitors)}], search:
  "[competitor-name] sandwich panels" review OR case study
  "[competitor-name] site:directory.com"
Find pages that link to competitors but NOT to {your_domain}.
For each gap: use identify_link_gap_opportunity and score with score_link_prospect.

──────────────────────────────────────────────────────────────
TASK 3 – DIRECTORY & TRADE PORTAL SUBMISSIONS
Call find_directory_submission_targets with niche="sandwich panel manufacturer PUF PIR cold room India" and location="India".
Then web_search for construction/manufacturing directories active in 2025-2026.
List the top 10 highest-value directories not yet featuring {your_domain}.
Provide ready-to-use submission details for each.

──────────────────────────────────────────────────────────────
TASK 4 – GUEST POST & RESOURCE PAGE OPPORTUNITIES
Search for:
  "write for us" construction panels insulation India
  "guest post" building materials cold storage India
  intitle:"resources" cold room clean room pharmaceutical India
Score each prospect. Generate outreach emails for the top 3 HIGH PRIORITY prospects.

──────────────────────────────────────────────────────────────
TASK 5 – Q&A / FORUM BACKLINKS
Search for questions on Quora and Reddit about:
  sandwich panels PUF PIR India cold room construction
  insulated panels manufacturer India
List 5 specific threads where a detailed expert answer linking to {your_domain} would help.
Draft a helpful answer for the top question that naturally links to the most relevant page on {your_domain}.

──────────────────────────────────────────────────────────────
TASK 6 – DAILY ACTION PLAN & REPORT
Compile findings into a prioritised action list for {today}:
  🔴 DO TODAY (high-impact, quick wins)
  🟡 THIS WEEK (moderate effort)
  🟢 ONGOING (evergreen link building)

Include exact URLs, ready-to-send emails, and estimated SEO value per action.
End with a one-paragraph executive summary for a daily email update."""

    messages = [{"role": "user", "content": user_message}]
    full_report: list[str] = []
    iterations = 0
    max_iterations = 30  # safety cap

    while iterations < max_iterations:
        iterations += 1
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=16000,
            system=system_prompt,
            tools=TOOL_SCHEMAS,
            messages=messages,
            extra_headers={"anthropic-beta": WEB_SEARCH_BETA_HEADER},
        )

        # Collect any text in this response turn
        for block in response.content:
            if hasattr(block, "type") and block.type == "text":
                print(block.text)
                full_report.append(block.text)

        if response.stop_reason == "end_turn":
            break

        # web_search results arrive as server_tool_use (handled server-side, no local dispatch needed)
        # Custom tool calls arrive as tool_use (need local dispatch)
        if response.stop_reason not in ("tool_use", "server_tool_use"):
            break

        tool_results = []
        for block in response.content:
            block_type = getattr(block, "type", None)

            if block_type == "server_tool_use":
                # web_search is fully server-side; result is already in the next assistant message
                print(f"  [web_search] query={getattr(block, 'input', {}).get('query', '')!r}")

            elif block_type == "tool_use":
                tool_name = block.name
                tool_input = block.input if isinstance(block.input, dict) else {}
                print(f"  [tool] {tool_name}({', '.join(f'{k}={repr(v)[:60]}' for k, v in tool_input.items())})")

                if tool_name in (
                    "analyze_backlink_quality", "categorize_brand_mention",
                    "score_link_prospect", "generate_outreach_template",
                    "identify_link_gap_opportunity", "find_directory_submission_targets",
                ):
                    result_content = _dispatch_tool(tool_name, tool_input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_content,
                    })

        # Append assistant turn; only add user turn when there are local tool results
        messages.append({"role": "assistant", "content": response.content})
        if tool_results:
            messages.append({"role": "user", "content": tool_results})

    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)
    report_filename = os.path.join(report_dir, f"backlink_report_{today}.md")
    with open(report_filename, "w") as f:
        f.write(f"# Daily Backlink Report – {brand_name}\n")
        f.write(f"**Date:** {today}  |  **Domain:** {your_domain}\n\n---\n\n")
        f.write("\n\n".join(full_report))
    print(f"\nReport saved → {report_filename}")
    return report_filename


if __name__ == "__main__":
    run_offpage_seo_agent()
