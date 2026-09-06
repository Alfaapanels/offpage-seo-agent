#!/usr/bin/env python3
"""Daily backlink building runner for alfaapanels.com"""

import anthropic
from anthropic import beta_tool
from datetime import date

client = anthropic.Anthropic()

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
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing", "quality", "durable"]
    negative_words = ["bad", "worst", "avoid", "scam", "terrible", "poor"]
    pos_score = sum(1 for w in positive_words if w in mention_text.lower())
    neg_score = sum(1 for w in negative_words if w in mention_text.lower())
    if pos_score > neg_score:
        sentiment = "Positive"
    elif neg_score > pos_score:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    mention_type = "Linked mention" if has_link else "Unlinked mention (link building opportunity!)"
    return f"Brand: {brand_name}\nType: {mention_type}\nSentiment: {sentiment}\nAction: {'Monitor' if has_link else 'Reach out to add your link'}"

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
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "suppliers", "manufacturers"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/guide page - high link value (+30)")
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
    link_type: str
) -> str:
    """Generate a personalized outreach email for link building.

    Args:
        prospect_name: Name of the website owner/editor.
        prospect_site: Their website name.
        their_page_topic: Topic of the page where you want a link.
        your_site: Your website name.
        your_content_url: URL of your content to be linked.
        link_type: Type: 'guest_post', 'broken_link', 'resource', 'mention'.
    """
    templates = {
        "broken_link": f"Subject: Broken link on your {their_page_topic} page\n\nHi {prospect_name},\n\nI noticed a broken link on your {their_page_topic} page on {prospect_site}.\n\nI have a comprehensive guide at {your_content_url} that would be a great replacement.\n\nWould you consider updating the link?\n\nBest,\nAlfa Panels Team",
        "guest_post": f"Subject: Guest Post Idea for {prospect_site}\n\nHi {prospect_name},\n\nI love your content on {prospect_site} about {their_page_topic}.\n\nI'd love to contribute a guest post on behalf of Alfa Panels (alfaapanels.com), a leading provider of decorative and architectural panels.\n\nWould you be open to a collaboration?\n\nBest,\nAlfa Panels Team",
        "resource": f"Subject: Resource suggestion for your {their_page_topic} page\n\nHi {prospect_name},\n\nYour resource page on {their_page_topic} is excellent! We at Alfa Panels have created {your_content_url} which might be very helpful for your readers interested in wall panels, cladding, and architectural finishes.\n\nWould you take a look?\n\nBest,\nAlfa Panels Team",
        "mention": f"Subject: You mentioned Alfa Panels - thank you!\n\nHi {prospect_name},\n\nThank you for mentioning Alfa Panels in your article about {their_page_topic}!\n\nWould you be open to linking directly to {your_content_url} for your readers' convenience?\n\nThanks,\nAlfa Panels Team"
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
    return f"LINK GAP OPPORTUNITY\nCompetitor: {competitor_domain}\nYour site: {your_domain}\nLinking page topic: {linking_page_topic}\n\nActions:\n1. Find what content earned {competitor_domain} this link\n2. Create better content on the same topic for {your_domain}\n3. Reach out to the linking page with your resource"


def run_daily_backlink_building():
    today = date.today().isoformat()
    domain = "alfaapanels.com"
    brand = "Alfa Panels"
    niche = "decorative wall panels architectural cladding building materials"
    competitors = [
        "decopanel.com",
        "panelsinternational.co.uk",
        "3acomposites.com",
        "alucobond.com"
    ]

    print(f"\n{'='*60}")
    print(f"Daily Backlink Building Run: {today}")
    print(f"Target: {domain}")
    print(f"{'='*60}\n")

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO strategist. Today is {today}.
Perform a complete off-page SEO backlink building session for: {domain}

Brand name: {brand}
Niche: {niche}
Competitors: {', '.join(competitors)}

Execute these tasks:

TASK 1 - Brand Mention Audit
Search for "{brand}" mentions online. Find unlinked mentions and link building opportunities.
Search query: "{brand}" -site:{domain}

TASK 2 - Fresh Link Building Opportunities
Find 5+ high-quality, relevant sites where we can build backlinks today:
- Architecture and interior design blogs accepting guest posts
- Building materials directories and supplier listings
- Decorative panels and cladding resource pages
- Construction industry forums and communities
- Home improvement and renovation websites

TASK 3 - Competitor Backlink Analysis
For each competitor, identify sites linking to them that don't link to {domain}.
Focus on: {', '.join(competitors)}

TASK 4 - Outreach Templates
Generate 3 ready-to-send personalized outreach emails for the best prospects found.

TASK 5 - Action Plan
Provide a prioritized list of exactly 10 specific backlink opportunities with:
- Target URL
- Outreach approach (guest post / resource page / directory / broken link)
- Estimated effort (low/medium/high)
- Expected impact (low/medium/high)

Be specific and actionable. Focus on opportunities that can be pursued TODAY."""
        }],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    report_filename = f"reports/backlinks_{today}.md"
    import os
    os.makedirs("reports", exist_ok=True)
    with open(report_filename, "w") as f:
        f.write(f"# Daily Backlink Building Report\n")
        f.write(f"**Date:** {today}  \n")
        f.write(f"**Domain:** {domain}  \n")
        f.write(f"**Brand:** {brand}  \n\n")
        f.write("---\n\n")
        f.write("\n\n".join(full_report))

    print(f"\nReport saved to: {report_filename}")
    return report_filename


if __name__ == "__main__":
    run_daily_backlink_building()
