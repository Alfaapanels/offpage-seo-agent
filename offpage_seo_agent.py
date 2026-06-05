import anthropic
import json
import os
from datetime import datetime

client = anthropic.Anthropic()

# ── Tool implementations ────────────────────────────────────────────────────

def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    quality_signals = []
    generic_anchors = ["click here", "website", "here", "link", "read more"]
    if anchor_text.lower() in generic_anchors:
        quality_signals.append("Warning: Generic anchor text - low SEO value")
    else:
        quality_signals.append(f"Good: Descriptive anchor text: '{anchor_text}'")
    toxic_signals = ["spam", "casino", "viagra", "adult", "pills"]
    if any(word in backlink_url.lower() for word in toxic_signals):
        quality_signals.append("TOXIC: Disavow this link immediately")
    else:
        quality_signals.append("Domain appears clean - no toxic signals")
    authority_domains = [".edu", ".gov", ".org"]
    if any(s in backlink_url for s in authority_domains):
        quality_signals.append("High authority domain type (edu/gov/org)")
    return "\n".join(quality_signals)


def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive_words = ["great", "best", "excellent", "recommend", "quality", "reliable", "top", "leading"]
    negative_words = ["bad", "worst", "avoid", "scam", "terrible", "poor", "fake"]
    pos_score = sum(1 for w in positive_words if w in mention_text.lower())
    neg_score = sum(1 for w in negative_words if w in mention_text.lower())
    if pos_score > neg_score:
        sentiment = "Positive"
    elif neg_score > pos_score:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    mention_type = "Linked mention" if has_link else "Unlinked mention (link building opportunity!)"
    action = "Monitor and engage" if has_link else "Reach out to convert to linked mention"
    return (
        f"Brand: {brand_name}\n"
        f"Type: {mention_type}\n"
        f"Sentiment: {sentiment}\n"
        f"Action: {action}"
    )


def score_link_prospect(page_url: str, page_title: str, page_content_snippet: str, your_niche: str) -> str:
    score = 0
    reasons = []
    niche_words = your_niche.lower().split()
    content_lower = (page_title + " " + page_content_snippet).lower()
    relevance = sum(1 for word in niche_words if word in content_lower)
    if relevance >= 3:
        score += 40
        reasons.append("High relevance to niche (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "top", "directory"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/guide/directory page (+30)")
    authority_signals = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority_signals):
        score += 30
        reasons.append("High authority domain (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH PRIORITY" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return (
        f"Prospect Score: {score}/100 - {priority}\n"
        f"URL: {page_url}\n"
        f"Reasons:\n" + "\n".join(f"  - {r}" for r in reasons)
    )


def generate_outreach_template(
    prospect_name: str,
    prospect_site: str,
    their_page_topic: str,
    your_site: str,
    your_content_url: str,
    link_type: str,
) -> str:
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I was reading your page about {their_page_topic} on {prospect_site} and noticed a broken link.\n\n"
            f"I have a comprehensive resource at {your_content_url} that would be an excellent replacement and adds real value for your readers.\n\n"
            f"Would you consider updating the link? Happy to provide any additional information.\n\n"
            f"Best regards,\n[Your Name]\n{your_site}"
        ),
        "guest_post": (
            f"Subject: Guest Post Pitch for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I'm a big fan of your content on {their_page_topic} at {prospect_site}. "
            f"I write for {your_site} and would love to contribute a guest post.\n\n"
            f"I can offer unique insights on topics your audience would love — happy to share 3 topic ideas if you're open to it.\n\n"
            f"Best regards,\n[Your Name]\n{your_site}"
        ),
        "resource": (
            f"Subject: Valuable resource for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is excellent! I recently published {your_content_url} which I think your readers would find very useful.\n\n"
            f"Would you consider adding it to your page? I believe it genuinely adds value alongside your existing resources.\n\n"
            f"Best regards,\n[Your Name]\n{your_site}"
        ),
        "mention": (
            f"Subject: Linking to {your_site} - quick request\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning {your_site} in your article about {their_page_topic}!\n\n"
            f"Would you be open to linking directly to {your_content_url}? It would make it easier for your readers to find us.\n\n"
            f"Thanks so much,\n[Your Name]\n{your_site}"
        ),
    }
    return templates.get(link_type, templates["resource"])


def identify_link_gap_opportunity(competitor_domain: str, your_domain: str, linking_page_topic: str) -> str:
    return (
        f"LINK GAP OPPORTUNITY IDENTIFIED\n"
        f"Competitor: {competitor_domain}\n"
        f"Your site: {your_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Action plan:\n"
        f"  1. Analyze what content earned {competitor_domain} this link\n"
        f"  2. Create superior content on the same topic for {your_domain}\n"
        f"  3. Reach out to the linking page with your better resource\n"
        f"  4. Track outreach status and follow up after 7 days"
    )


# ── Tool schema definitions ─────────────────────────────────────────────────

CUSTOM_TOOLS = [
    {
        "name": "analyze_backlink_quality",
        "description": "Evaluate quality of a backlink pointing to a URL.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Your target URL"},
                "backlink_url": {"type": "string", "description": "The URL linking to you"},
                "anchor_text": {"type": "string", "description": "The anchor text used in the link"},
            },
            "required": ["url", "backlink_url", "anchor_text"],
        },
    },
    {
        "name": "categorize_brand_mention",
        "description": "Categorize a brand mention as linked/unlinked and determine sentiment.",
        "input_schema": {
            "type": "object",
            "properties": {
                "mention_text": {"type": "string", "description": "The text containing the brand mention"},
                "brand_name": {"type": "string", "description": "Your brand or website name"},
            },
            "required": ["mention_text", "brand_name"],
        },
    },
    {
        "name": "score_link_prospect",
        "description": "Score a potential link building prospect page.",
        "input_schema": {
            "type": "object",
            "properties": {
                "page_url": {"type": "string", "description": "URL of the prospect page"},
                "page_title": {"type": "string", "description": "Title of the page"},
                "page_content_snippet": {"type": "string", "description": "Short snippet of page content"},
                "your_niche": {"type": "string", "description": "Your website niche/topic"},
            },
            "required": ["page_url", "page_title", "page_content_snippet", "your_niche"],
        },
    },
    {
        "name": "generate_outreach_template",
        "description": "Generate a personalized outreach email for link building.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prospect_name": {"type": "string", "description": "Name of the website owner/editor"},
                "prospect_site": {"type": "string", "description": "Their website name"},
                "their_page_topic": {"type": "string", "description": "Topic of the page where you want a link"},
                "your_site": {"type": "string", "description": "Your website name"},
                "your_content_url": {"type": "string", "description": "URL of your content to be linked"},
                "link_type": {
                    "type": "string",
                    "enum": ["guest_post", "broken_link", "resource", "mention"],
                    "description": "Type of link building approach",
                },
            },
            "required": ["prospect_name", "prospect_site", "their_page_topic", "your_site", "your_content_url", "link_type"],
        },
    },
    {
        "name": "identify_link_gap_opportunity",
        "description": "Identify if a competitor backlink is a link gap opportunity for your site.",
        "input_schema": {
            "type": "object",
            "properties": {
                "competitor_domain": {"type": "string", "description": "Competitor's domain"},
                "your_domain": {"type": "string", "description": "Your domain"},
                "linking_page_topic": {"type": "string", "description": "Topic of the page linking to competitor"},
            },
            "required": ["competitor_domain", "your_domain", "linking_page_topic"],
        },
    },
]

BUILT_IN_TOOLS = [
    {"type": "web_search_20260209", "name": "web_search"},
    {"type": "web_fetch_20260209", "name": "web_fetch"},
]

ALL_TOOLS = CUSTOM_TOOLS + BUILT_IN_TOOLS

TOOL_DISPATCH = {
    "analyze_backlink_quality": analyze_backlink_quality,
    "categorize_brand_mention": categorize_brand_mention,
    "score_link_prospect": score_link_prospect,
    "generate_outreach_template": generate_outreach_template,
    "identify_link_gap_opportunity": identify_link_gap_opportunity,
}


# ── Agentic loop ────────────────────────────────────────────────────────────

def execute_tool(name: str, inputs: dict) -> str:
    fn = TOOL_DISPATCH.get(name)
    if fn:
        return fn(**inputs)
    return f"Tool '{name}' is a built-in tool handled by the API."


def run_agentic_loop(initial_messages: list, model: str = "claude-opus-4-8", max_tokens: int = 16000) -> list:
    messages = list(initial_messages)
    text_blocks = []

    for iteration in range(30):
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            tools=ALL_TOOLS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        for block in response.content:
            if hasattr(block, "text"):
                print(block.text)
                text_blocks.append(block.text)

        if response.stop_reason == "end_turn":
            break

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    return text_blocks


# ── Main agent ──────────────────────────────────────────────────────────────

def run_offpage_seo_agent(your_domain: str, brand_name: str, niche: str, competitors: list) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\nOff-Page SEO Agent — {your_domain} — {today}")
    print("=" * 60)

    messages = [
        {
            "role": "user",
            "content": f"""You are an expert off-page SEO strategist. Today is {today}.

Perform a complete off-page SEO session for: {your_domain}
Brand name: {brand_name}
Niche: {niche}
Competitors: {', '.join(competitors)}

Complete ALL five tasks below, using web_search and web_fetch to gather real data, then use the provided tools to analyse and score findings.

───────────────────────────────────────────────────
TASK 1 — Brand Mention Audit
Search for unlinked mentions of "{brand_name}" across the web.
- Search query: '"{brand_name}" -site:{your_domain}'
- Find at least 5 unlinked mentions and categorize each using categorize_brand_mention.
- Prioritize positive mentions for outreach.

TASK 2 — Competitor Backlink Research & Link Gap Analysis
For each competitor ({', '.join(competitors)}):
- Search: 'site:{competitor} OR link:{competitor} panels facade'
- Identify pages linking to competitors but not to {your_domain}.
- Use identify_link_gap_opportunity for the top 3 gaps found.

TASK 3 — Link Building Prospect Discovery
Find high-quality link building targets in the {niche} niche:
- Search for: '{niche} resource page OR "useful links" OR "recommended suppliers"'
- Search for: '{niche} blog "write for us" OR "guest post"'
- Search for: '{niche} directory submit site'
- Score each prospect using score_link_prospect.
- Analyse backlink quality signals with analyze_backlink_quality where relevant.

TASK 4 — Personalised Outreach Templates
For the top 3 prospects discovered in Task 3, generate tailored outreach emails using generate_outreach_template.
Use the most appropriate link_type for each: guest_post, broken_link, resource, or mention.

TASK 5 — Daily Action Plan
Provide a prioritised list of:
1. The 5 best backlink opportunities to pursue today (with URLs and contact strategy)
2. The 3 unlinked mentions to convert this week
3. Any quick wins (directories, forums, Q&A sites like Quora/Reddit relevant to {niche})
4. This week's content recommendation to attract natural backlinks

Format your final report clearly with sections and bullet points so it can be acted on immediately.""",
        }
    ]

    text_blocks = run_agentic_loop(messages)

    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"seo_report_{today}.md")
    with open(report_path, "w") as f:
        f.write(f"# Off-Page SEO Report: {your_domain}\n")
        f.write(f"**Date:** {today}\n\n")
        f.write("\n\n".join(text_blocks))

    print(f"\nReport saved to: {report_path}")
    return report_path


if __name__ == "__main__":
    run_offpage_seo_agent(
        your_domain="alfaapanels.com",
        brand_name="Alfa Panels",
        niche="aluminum composite panels building facade cladding architectural panels",
        competitors=[
            "alucobond.com",
            "reynobond.com",
            "alpolic.com",
            "dibond.com",
        ],
    )
