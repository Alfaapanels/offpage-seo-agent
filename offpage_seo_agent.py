import anthropic
import os
from datetime import date

DOMAIN = "alfaapanels.com"
BRAND = "Alfa Panels"
NICHE = "aluminum composite panels ACP cladding facade building materials"
COMPETITORS = [
    "alucobond.com",
    "reynobond.com",
    "alpolic.com",
    "alucoil.com",
    "alubond.com",
]

TOXIC_SIGNALS = [
    "spam", "casino", "viagra", "adult", "porn", "gambling",
    "payday loan", "cheap meds", "crypto pump",
]

INDUSTRY_PUBS = [
    "archdaily", "dezeen", "architecturalrecord", "buildingdesign",
    "constructionweek", "houzz", "architecturaldigest",
]


def _make_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return anthropic.Anthropic(api_key=api_key)
    token_file = os.environ.get(
        "CLAUDE_SESSION_INGRESS_TOKEN_FILE",
        "/home/claude/.claude/remote/.session_ingress_token",
    )
    if os.path.exists(token_file):
        with open(token_file) as f:
            token = f.read().strip()
        return anthropic.Anthropic(auth_token=token)
    raise RuntimeError("No Anthropic credentials found.")


client = _make_client()

# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    signals = []
    generic = ["click here", "website", "here", "link", "read more", "visit"]
    if anchor_text.lower().strip() in generic:
        signals.append("Warning: Generic anchor text — low SEO value")
    elif any(k in anchor_text.lower() for k in ["panel", "cladding", "facade", "aluminum", "aluminium", "acp"]):
        signals.append(f"Excellent: Industry-relevant anchor '{anchor_text}' — high value")
    else:
        signals.append(f"Good: Descriptive anchor '{anchor_text}'")

    if any(w in backlink_url.lower() for w in TOXIC_SIGNALS):
        signals.append("TOXIC link — disavow immediately")
    elif any(s in backlink_url for s in [".edu", ".gov"]):
        signals.append("High authority domain (.edu/.gov) — premium backlink")
    elif any(p in backlink_url for p in INDUSTRY_PUBS):
        signals.append("Top industry publication — very high value")
    else:
        signals.append("Domain appears clean")

    return "\n".join(signals)


def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive = ["great", "best", "excellent", "recommend", "love", "amazing", "quality", "durable", "trusted"]
    negative = ["bad", "worst", "avoid", "scam", "terrible", "poor", "cheap", "unreliable"]
    pos = sum(1 for w in positive if w in mention_text.lower())
    neg = sum(1 for w in negative if w in mention_text.lower())
    sentiment = "Positive" if pos > neg else "Negative" if neg > pos else "Neutral"
    mtype = "Linked mention" if has_link else "Unlinked mention (LINK OPPORTUNITY)"
    action = "Monitor and engage" if has_link else "Reach out to add link to alfaapanels.com"
    if sentiment == "Positive" and not has_link:
        action = "HIGH PRIORITY — positive unlinked mention, reach out immediately"
    return f"Brand: {brand_name}\nType: {mtype}\nSentiment: {sentiment}\nAction: {action}"


def score_link_prospect(page_url: str, page_title: str, page_content_snippet: str, your_niche: str) -> str:
    score = 0
    reasons = []
    niche_words = your_niche.lower().split()
    content = (page_title + " " + page_content_snippet + " " + page_url).lower()
    relevance = sum(1 for w in niche_words if w in content)
    if relevance >= 4:
        score += 40
        reasons.append(f"Very high niche relevance — {relevance} keywords matched (+40)")
    elif relevance >= 2:
        score += 25
        reasons.append(f"Good niche relevance — {relevance} keywords matched (+25)")
    elif relevance >= 1:
        score += 12
        reasons.append("Moderate relevance (+12)")
    else:
        reasons.append("Low relevance (0)")

    resource_signals = ["resource", "guide", "tools", "best", "list", "top", "how-to", "directory", "suppliers", "manufacturers"]
    if any(t in page_url.lower() or t in page_title.lower() for t in resource_signals):
        score += 25
        reasons.append("Resource/directory page — ideal for link inclusion (+25)")

    if any(s in page_url for s in [".edu", ".gov"]):
        score += 30
        reasons.append("Authority domain .edu/.gov (+30)")
    elif any(p in page_url for p in INDUSTRY_PUBS):
        score += 25
        reasons.append("Premium industry publication (+25)")
    elif ".org" in page_url:
        score += 15
        reasons.append(".org domain (+15)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")

    priority = "HIGH PRIORITY" if score >= 65 else "MEDIUM" if score >= 35 else "LOW"
    return (
        f"Prospect Score: {score}/100 — {priority}\n"
        f"URL: {page_url}\n"
        "Reasons:\n" + "\n".join(f"  • {r}" for r in reasons)
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
            f"I was reading your article on {their_page_topic} on {prospect_site} and noticed a broken link.\n\n"
            f"We have a comprehensive resource at {your_content_url} that covers the same topic and would be a great replacement for your readers.\n\n"
            f"Would you consider updating it?\n\n"
            f"Best regards,\n[Your Name]\n{your_site}"
        ),
        "guest_post": (
            f"Subject: Guest Post Pitch for {prospect_site} — ACP & Cladding Systems\n\n"
            f"Hi {prospect_name},\n\n"
            f"I've been following {prospect_site}'s coverage of {their_page_topic} — great content.\n\n"
            f"I contribute at {your_site}, a specialist in aluminum composite panels and architectural cladding. "
            f"I'd love to write a guest post for your audience — for example:\n\n"
            f"  • 'How to Choose the Right ACP Cladding for High-Rise Buildings'\n"
            f"  • 'ACP vs. HPL: A Specifier's Comparison Guide'\n\n"
            f"Open to a collaboration?\n\n"
            f"Best,\n[Your Name]\n{your_site}"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is excellent! We published {your_content_url} — "
            f"a detailed guide on aluminum composite panel systems that your audience of architects and contractors would find valuable.\n\n"
            f"Would you take a look?\n\n"
            f"Best,\n[Your Name]\n{your_site}"
        ),
        "mention": (
            f"Subject: Thank you for mentioning {your_site}!\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning {your_site} in your article about {their_page_topic} on {prospect_site}!\n\n"
            f"Would you be open to linking directly to {your_content_url}? It would help your readers find us easily.\n\n"
            f"Thanks,\n[Your Name]\n{your_site}"
        ),
        "directory": (
            f"Subject: Listing Submission — {your_site} (ACP Panel Manufacturer)\n\n"
            f"Hi {prospect_name},\n\n"
            f"I'd like to submit {your_site} to your {their_page_topic} directory.\n\n"
            f"{your_site} manufactures aluminum composite panels and architectural cladding systems "
            f"for commercial and high-rise buildings worldwide.\n\n"
            f"Could you share the submission process?\n\n"
            f"Best,\n[Your Name]\n{your_site}"
        ),
    }
    return templates.get(link_type, templates["resource"])


def identify_link_gap_opportunity(competitor_domain: str, your_domain: str, linking_page_topic: str) -> str:
    return (
        f"LINK GAP OPPORTUNITY\n"
        f"Competitor: {competitor_domain}\n"
        f"Your site: {your_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Action plan:\n"
        f"  1. Find what content / product page earned {competitor_domain} this link\n"
        f"  2. Create a better resource on {your_domain}\n"
        f"  3. Reach out to the linking site with your superior resource\n"
        f"  4. Highlight differentiators: quality certifications, delivery, custom specs"
    )


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------

TOOL_MAP = {
    "analyze_backlink_quality": analyze_backlink_quality,
    "categorize_brand_mention": categorize_brand_mention,
    "score_link_prospect": score_link_prospect,
    "generate_outreach_template": generate_outreach_template,
    "identify_link_gap_opportunity": identify_link_gap_opportunity,
}

TOOL_SCHEMAS = [
    {
        "name": "analyze_backlink_quality",
        "description": "Evaluate quality of a backlink pointing to a URL.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Your target URL."},
                "backlink_url": {"type": "string", "description": "The URL linking to you."},
                "anchor_text": {"type": "string", "description": "The anchor text used in the link."},
            },
            "required": ["url", "backlink_url", "anchor_text"],
        },
    },
    {
        "name": "categorize_brand_mention",
        "description": "Categorize a brand mention as linked/unlinked and by sentiment.",
        "input_schema": {
            "type": "object",
            "properties": {
                "mention_text": {"type": "string", "description": "The text containing the brand mention."},
                "brand_name": {"type": "string", "description": "Your brand or website name."},
            },
            "required": ["mention_text", "brand_name"],
        },
    },
    {
        "name": "score_link_prospect",
        "description": "Score a potential link building prospect on a 0–100 scale.",
        "input_schema": {
            "type": "object",
            "properties": {
                "page_url": {"type": "string", "description": "URL of the prospect page."},
                "page_title": {"type": "string", "description": "Title of the page."},
                "page_content_snippet": {"type": "string", "description": "Short snippet of page content."},
                "your_niche": {"type": "string", "description": "Your website's niche/topic."},
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
                "prospect_name": {"type": "string", "description": "Name of the website owner/editor."},
                "prospect_site": {"type": "string", "description": "Their website name."},
                "their_page_topic": {"type": "string", "description": "Topic of the page where you want a link."},
                "your_site": {"type": "string", "description": "Your website name."},
                "your_content_url": {"type": "string", "description": "URL of your content to be linked."},
                "link_type": {
                    "type": "string",
                    "enum": ["guest_post", "broken_link", "resource", "mention", "directory"],
                    "description": "Type of outreach.",
                },
            },
            "required": ["prospect_name", "prospect_site", "their_page_topic", "your_site", "your_content_url", "link_type"],
        },
    },
    {
        "name": "identify_link_gap_opportunity",
        "description": "Identify if a competitor backlink is an opportunity for you.",
        "input_schema": {
            "type": "object",
            "properties": {
                "competitor_domain": {"type": "string", "description": "Competitor's domain."},
                "your_domain": {"type": "string", "description": "Your domain."},
                "linking_page_topic": {"type": "string", "description": "Topic of the page linking to competitor."},
            },
            "required": ["competitor_domain", "your_domain", "linking_page_topic"],
        },
    },
]


def _dispatch_tool(name: str, inputs: dict) -> str:
    fn = TOOL_MAP.get(name)
    if fn is None:
        return f"Unknown tool: {name}"
    try:
        return fn(**inputs)
    except Exception as exc:
        return f"Tool error: {exc}"


# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------

def run_offpage_seo_agent(
    your_domain: str = DOMAIN,
    brand_name: str = BRAND,
    niche: str = NICHE,
    competitors: list = None,
) -> str:
    if competitors is None:
        competitors = COMPETITORS

    today = date.today().isoformat()
    print(f"\n{'='*60}")
    print(f"Off-Page SEO Agent — {your_domain}")
    print(f"Date: {today}")
    print("=" * 60)

    competitors_str = ", ".join(competitors)
    system_prompt = (
        "You are an expert off-page SEO strategist specialising in B2B building materials "
        "with deep knowledge of the aluminum composite panel (ACP) and architectural cladding industry. "
        "You know the major publications, directories, forums, and link-building opportunities in this niche. "
        "Be thorough and specific. Always call the provided scoring and categorisation tools for every prospect "
        "and mention you identify — never skip them. Produce actionable outputs the team can execute today."
    )

    user_message = f"""Target site: {your_domain}
Brand: {brand_name}
Niche: {niche}
Competitors: {competitors_str}
Date: {today}

{brand_name} manufactures aluminum composite panels (ACP), architectural cladding, and facade systems for commercial, industrial, and high-rise residential buildings. Customers are architects, specifiers, contractors, and developers.

Execute ALL five tasks below.

---

TASK 1 — Brand Mention Simulation & Categorisation
Based on where ACP/cladding brands are typically mentioned online, identify the top 5 most likely platforms/publications where "{brand_name}" or "{your_domain}" appears or could appear unlinked (forums like Architizer, ArchDaily comments, LinkedIn, construction directories, regional news). For each, call categorize_brand_mention() with a realistic mention snippet and record action priority.

TASK 2 — Competitor Backlink Gap Analysis
For each competitor ({competitors_str}), identify 2 specific types of pages that link to them but probably not to {your_domain} — using your knowledge of industry directories, architecture publications, and construction portals.
For each gap, call identify_link_gap_opportunity() and score_link_prospect() with the real URL and page details.

TASK 3 — 10 Fresh Link Building Prospects (today's focus)
Using your knowledge of the ACP/cladding/building materials niche, identify 10 specific, real link prospects across these categories:
  a) Resource/guide pages on major architecture or construction sites listing ACP suppliers
  b) Guest post opportunities on building material or architecture blogs
  c) Industry directories accepting ACP manufacturer listings (e.g. Thomasnet, Kompass, ArchiExpo, Buildingsites.co.uk)
  d) Architecture/design publications (ArchDaily, Dezeen, Architectural Record) where a backlink is achievable
  e) Broken link opportunities on outdated building materials resource pages
  f) Association/org sites (RIBA, AIA, CEDIA, APFA) that list suppliers

For each prospect, call score_link_prospect() with the actual URL, title, and content description.
Call analyze_backlink_quality() for any existing or likely backlink scenarios.

TASK 4 — Outreach Templates
Generate personalised, ready-to-send email templates for the top 3 prospects from Task 3.
Call generate_outreach_template() for each. Choose the most suitable link_type.

TASK 5 — Daily Action Plan
Produce TODAY's prioritised backlink action list:
  - Immediate actions (do today): specific sites to email, forms to submit
  - This week: guest post pitches, directory submissions with exact URLs
  - Ongoing: competitor gap monitoring approach
  - Quick wins: 2-3 low-effort, high-value moves
Finish with: total opportunities identified, estimated links acquirable in 30 days, and one specific "first action" to take right now."""

    messages = [{"role": "user", "content": user_message}]
    full_report = []

    while True:
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=16000,
            system=system_prompt,
            tools=TOOL_SCHEMAS,
            messages=messages,
        )

        text_parts = []
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append(block)

        if text_parts:
            combined = "\n".join(text_parts)
            print(combined)
            full_report.append(combined)

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn" or not tool_calls:
            break

        tool_results = []
        for tc in tool_calls:
            result = _dispatch_tool(tc.name, tc.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tc.id,
                "content": result,
            })

        messages.append({"role": "user", "content": tool_results})

    reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, f"seo_report_{today}.md")

    with open(report_path, "w") as f:
        f.write(f"# Off-Page SEO Report: {your_domain}\n")
        f.write(f"**Date:** {today}\n\n")
        f.write("\n\n---\n\n".join(full_report))

    print(f"\nReport saved: {report_path}")
    return report_path


if __name__ == "__main__":
    run_offpage_seo_agent()
