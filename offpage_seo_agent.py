"""
Off-Page SEO Agent — core agent powered by Claude claude-opus-4-6.

Performs daily backlink discovery, gap analysis, and outreach generation
for alfaapanels.com (or any configured domain).
"""

import os
import anthropic
from anthropic import beta_tool

client = anthropic.Anthropic()


# ---------------------------------------------------------------------------
# Tools available to the agent
# ---------------------------------------------------------------------------

@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to a URL.

    Args:
        url: Your target URL.
        backlink_url: The URL linking to you.
        anchor_text: The anchor text used in the link.
    """
    quality_signals = []
    exact_match_keywords = ["click here", "website", "here", "link"]
    if anchor_text.lower() in exact_match_keywords:
        quality_signals.append("Warning: Generic anchor text - low value")
    else:
        quality_signals.append(f"Good: Descriptive anchor: '{anchor_text}'")
    if any(word in backlink_url.lower() for word in ["spam", "casino", "viagra"]):
        quality_signals.append("TOXIC link - disavow recommended")
    else:
        quality_signals.append("Domain appears clean")
    return "\n".join(quality_signals)


@beta_tool
def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    """Categorize a brand mention as linked/unlinked and sentiment.

    Args:
        mention_text: The text containing the brand mention.
        brand_name: Your brand or website name.
    """
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing", "quality", "reliable"]
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
    return (
        f"Brand: {brand_name}\n"
        f"Type: {mention_type}\n"
        f"Sentiment: {sentiment}\n"
        f"Action: {'Monitor' if has_link else 'Reach out to add your link'}"
    )


@beta_tool
def score_link_prospect(page_url: str, page_title: str, page_content_snippet: str, your_niche: str) -> str:
    """Score a potential link building prospect.

    Args:
        page_url: URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: Short snippet of page content.
        your_niche: Your website's niche/topic.
    """
    score = 0
    reasons = []
    niche_words = your_niche.lower().split()
    content_lower = (page_title + " " + page_content_snippet).lower()
    relevance = sum(1 for word in niche_words if word in content_lower)
    if relevance >= 3:
        score += 40
        reasons.append("High relevance to your niche (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "review", "directory"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/guide/directory page - high link value (+30)")
    authority_signals = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority_signals):
        score += 30
        reasons.append("High authority domain (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH PRIORITY" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Prospect Score: {score}/100 - {priority}\nURL: {page_url}\nReasons:\n" + "\n".join(reasons)


@beta_tool
def generate_outreach_template(
    prospect_name: str,
    prospect_site: str,
    their_page_topic: str,
    your_site: str,
    your_content_url: str,
    link_type: str,
) -> str:
    """Generate a personalized outreach email for link building.

    Args:
        prospect_name: Name of the website owner/editor.
        prospect_site: Their website name.
        their_page_topic: Topic of the page where you want a link.
        your_site: Your website name.
        your_content_url: URL of your content to be linked.
        link_type: Type: 'guest_post', 'broken_link', 'resource', 'mention', 'directory'.
    """
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I was reading your {their_page_topic} page on {prospect_site} and noticed a broken link.\n\n"
            f"I have a comprehensive guide at {your_content_url} on {your_site} that would be a perfect replacement.\n\n"
            f"Would you consider updating the link? Happy to share the exact URL that's broken.\n\n"
            f"Best regards,\n[Your Name] — {your_site}"
        ),
        "guest_post": (
            f"Subject: Guest Post Pitch for {prospect_site} — Solar Energy Expert\n\n"
            f"Hi {prospect_name},\n\n"
            f"I'm a big fan of your content on {their_page_topic} over at {prospect_site}.\n\n"
            f"I write for {your_site} and would love to contribute an original, in-depth guest post for your audience. "
            f"A few topic ideas:\n"
            f"  • How to choose the right solar panel type for your roof\n"
            f"  • The true ROI of residential solar in 2025\n"
            f"  • Common solar installation mistakes and how to avoid them\n\n"
            f"Would you be open to a collaboration? I can send over a full outline first.\n\n"
            f"Best regards,\n[Your Name] — {your_site}"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} at {prospect_site} is really valuable — I've shared it with colleagues.\n\n"
            f"I recently published {your_content_url} which covers [topic] in detail and might be a great addition for your readers.\n\n"
            f"Would you take a look and consider adding it?\n\n"
            f"Best regards,\n[Your Name] — {your_site}"
        ),
        "mention": (
            f"Subject: You mentioned {your_site} — thank you!\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning {your_site} in your article about {their_page_topic}!\n\n"
            f"Would you be open to turning that mention into a direct link to {your_content_url}? "
            f"It would make it even easier for your readers to find the resource.\n\n"
            f"Thanks again!\n[Your Name] — {your_site}"
        ),
        "directory": (
            f"Subject: {your_site} Submission — Solar Panel Supplier\n\n"
            f"Hi {prospect_name},\n\n"
            f"I'd like to submit {your_site} to your {their_page_topic} directory.\n\n"
            f"Alfa Panels is a professional solar panel supplier offering residential and commercial photovoltaic solutions. "
            f"Our listing URL: {your_content_url}\n\n"
            f"Please let me know if you need any additional information for the submission.\n\n"
            f"Best regards,\n[Your Name] — {your_site}"
        ),
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def identify_link_gap_opportunity(competitor_domain: str, your_domain: str, linking_page_topic: str) -> str:
    """Identify if a competitor backlink is an opportunity for you.

    Args:
        competitor_domain: Competitor's domain.
        your_domain: Your domain.
        linking_page_topic: Topic of the page linking to competitor.
    """
    return (
        f"LINK GAP OPPORTUNITY\n"
        f"Competitor   : {competitor_domain}\n"
        f"Your site    : {your_domain}\n"
        f"Linking topic: {linking_page_topic}\n\n"
        f"Action plan:\n"
        f"1. Identify exactly which content on {competitor_domain} earned this link\n"
        f"2. Create a higher-quality, more comprehensive page on {your_domain} covering the same topic\n"
        f"3. Reach out to the linking page with your superior resource"
    )


@beta_tool
def record_backlink_opportunity(
    url: str,
    link_type: str,
    anchor_text: str,
    prospect_score: int,
    strategy: str,
    notes: str,
) -> str:
    """Record a discovered backlink opportunity to the local tracker.

    Args:
        url: The prospect page URL.
        link_type: guest_post | broken_link | resource | mention | directory | forum
        anchor_text: Suggested anchor text for the link.
        prospect_score: Estimated score 0-100.
        strategy: Which daily strategy found this.
        notes: Any extra context about the opportunity.
    """
    import backlink_tracker as bt
    if bt.already_tracked(url):
        return f"SKIPPED — already tracked: {url}"
    entry = bt.add_opportunity(url, link_type, anchor_text, prospect_score, strategy, notes)
    return f"RECORDED opportunity #{entry['id']}: {url} (score={prospect_score}, type={link_type})"


# ---------------------------------------------------------------------------
# Agent runner
# ---------------------------------------------------------------------------

def run_offpage_seo_agent(
    your_domain: str,
    brand_name: str,
    niche: str,
    competitors: list,
    daily_strategy: dict | None = None,
) -> list[str]:
    """Run the off-page SEO agent and return the collected report blocks."""
    strategy_context = ""
    if daily_strategy:
        strategy_context = (
            f"\n\nTODAY'S FOCUS: {daily_strategy['name']}\n"
            f"Goal: {daily_strategy['description']}\n\n"
            f"Execute these specific strategies in order:\n"
            + "\n".join(f"  {i+1}. {s}" for i, s in enumerate(daily_strategy["strategies"]))
        )

    print(f"\nStarting Off-Page SEO Agent for: {your_domain}")
    if daily_strategy:
        print(f"Strategy: {daily_strategy['name']}")
    print("=" * 60)

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            record_backlink_opportunity,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO strategist building high-quality, relevant backlinks.

Target website : {your_domain}
Brand name     : {brand_name}
Niche          : {niche}
Competitors    : {', '.join(competitors)}
{strategy_context}

MANDATORY WORKFLOW
==================
For every opportunity you discover:
1. Use score_link_prospect to evaluate it
2. Use record_backlink_opportunity to save it (this prevents duplicate work)
3. Use generate_outreach_template to draft the email

CORE TASKS (complete all 5)
============================
TASK 1 — Brand Mention Audit
Search: "{brand_name}" -site:{your_domain}
Also try: "alfaapanels" -site:{your_domain}
Find unlinked mentions → categorize with categorize_brand_mention → record opportunities.

TASK 2 — Competitor Backlink Gap
For each competitor in [{', '.join(competitors[:3])}]:
  • Search: link:{competitor} solar panels
  • Find resource/blog pages linking to them
  • Score each with score_link_prospect
  • Use identify_link_gap_opportunity
  • Record top 3 per competitor

TASK 3 — Today's Strategy Execution
{strategy_context if strategy_context else "Find resource pages, guest post opportunities, and broken links in the solar/renewable energy niche."}

TASK 4 — Outreach Templates
Generate ready-to-send email templates for the top 5 highest-scoring prospects you recorded today.

TASK 5 — Daily Action Summary
Produce a structured Markdown report with:
## Daily Backlink Building Report — {your_domain}
### Opportunities Found (table: URL | Type | Score | Anchor Text)
### Top 5 Outreach Emails
### Recommended Next Steps (bullet list)
### Running Totals (from tracker)
""",
        }],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    return full_report


if __name__ == "__main__":
    from config import SITE_CONFIG
    run_offpage_seo_agent(
        your_domain=SITE_CONFIG["domain"],
        brand_name=SITE_CONFIG["brand_name"],
        niche=SITE_CONFIG["niche"],
        competitors=SITE_CONFIG["competitors"],
    )
