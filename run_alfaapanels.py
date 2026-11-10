#!/usr/bin/env python3.13
"""Daily backlink building runner for alfaapanels.com"""

import os
import sys
from datetime import datetime

# Ensure we import the right anthropic
sys.path.insert(0, '/usr/local/lib/python3.13/site-packages')

import anthropic
from anthropic import beta_tool

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
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing", "quality", "reliable"]
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
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "directory", "supplier"]
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
        "broken_link": f"Subject: Broken link on your {their_page_topic} page\n\nHi {prospect_name},\n\nI was browsing your {their_page_topic} page on {prospect_site} and noticed a broken link.\n\nAlfaa Panels has a comprehensive resource at {your_content_url} that could be a great replacement and would genuinely help your readers.\n\nWould you consider updating the link?\n\nBest regards,\nAlfaa Panels Team\n{your_site}",
        "guest_post": f"Subject: Guest Post Idea for {prospect_site} - Insulated Panel Systems\n\nHi {prospect_name},\n\nI've been following your content on {prospect_site} about {their_page_topic} and find it very valuable.\n\nI'm from Alfaa Panels ({your_site}), a leading manufacturer of insulated sandwich panels and pre-engineered buildings since 1992.\n\nI'd love to contribute a guest post on topics like energy-efficient building panels, cold room solutions, or PEB construction best practices.\n\nWould you be open to a collaboration?\n\nBest regards,\nAlfaa Panels Team",
        "resource": f"Subject: Resource suggestion for your {their_page_topic} page\n\nHi {prospect_name},\n\nYour resource page on {their_page_topic} is excellent! I noticed it could benefit from a resource on insulated sandwich panels and pre-engineered buildings.\n\nAlfaa Panels has created {your_content_url} which covers this topic comprehensively and might add value for your readers.\n\nWould you take a look?\n\nBest regards,\nAlfaa Panels Team\n{your_site}",
        "mention": f"Subject: You mentioned Alfaa Panels - thank you!\n\nHi {prospect_name},\n\nThank you for mentioning Alfaa Panels in your article about {their_page_topic}!\n\nWould you be open to linking directly to {your_content_url} so your readers can easily find more details?\n\nThanks,\nAlfaa Panels Team\n{your_site}"
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
    return f"LINK GAP OPPORTUNITY\nCompetitor: {competitor_domain}\nYour site: {your_domain}\nLinking page topic: {linking_page_topic}\n\nActions:\n1. Find what content earned {competitor_domain} this link\n2. Create better content on the same topic for {your_domain}\n3. Reach out to the linking page with your Alfaa Panels resource\n4. Highlight unique value: 30+ years experience, ISO certifications, pan-India delivery"


def run_backlink_agent():
    domain = "alfaapanels.com"
    brand = "Alfaa Panels"
    niche = "insulated sandwich panels pre-engineered buildings cold room panels PUF panels construction India"
    competitors = [
        "kingspanpanels.com",
        "thermopanels.in",
        "alfapeb.com",
        "rockwoolgroup.com"
    ]

    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\nOff-Page SEO Backlink Agent for: {domain}")
    print(f"Date: {today}")
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
            {"type": "web_search_20260209", "name": "web_search"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO strategist working for {brand} ({domain}).

Company background:
- Alfaa Panels (Alfaa PEB Ltd) is a leading Indian manufacturer of insulated sandwich panels, PUF/PIR panels, rockwool panels, cold room panels, clean room panels, and pre-engineered buildings.
- Founded in 1992, headquartered in Bengaluru, Karnataka, India.
- Serves industrial buildings, warehouses, cold storage, food processing, pharmaceutical cleanrooms, and commercial construction.
- Niche: {niche}
- Competitors: {', '.join(competitors)}

Today's date: {today}

Execute these backlink building tasks:

TASK 1 - Brand Mention Audit
Search for "{brand}" and "Alfaa Panels" mentions online. Use web_search to find unlinked mentions.
Search queries to try:
- "{brand}" -site:{domain}
- "Alfaa Panels" construction India
- "alfaa panels" review

For each mention found, use categorize_brand_mention tool to classify it.

TASK 2 - Competitor Backlink Research
For each competitor below, use web_search to find sites that link to them:
- Search: link:kingspanpanels.com insulated panels
- Search: "alfapeb.com" OR "alfa peb" India construction site
Find sites linking to competitors but likely not to {domain}. Use identify_link_gap_opportunity for each.

TASK 3 - Link Building Opportunities
Use web_search to find these opportunities:
a) Resource pages: search "insulated panels" "resources" OR "links" India
b) Guest post opportunities: search "insulated sandwich panels" "write for us" OR "guest post"
c) Industry directories: search "construction materials directory India" OR "building materials suppliers India directory"
d) Forum/Q&A: search site:quora.com "insulated panels India" OR "cold room panels India"
e) Wikipedia/wikis: search site:en.wikipedia.org "sandwich panel"

For each prospect found, use score_link_prospect tool to evaluate it.

TASK 4 - Outreach Templates
Generate personalized outreach emails for the top 3 prospects found, using generate_outreach_template.

TASK 5 - Final Report
Create a prioritized 30-day action plan with:
- Top 10 backlink opportunities with URLs and contact approach
- 5 guest post targets with proposed topics
- Brand mention conversion opportunities
- Directory submission targets
- Estimated timeline and effort for each action"""
        }],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    report_filename = f"backlink_report_{today}.md"
    with open(report_filename, "w") as f:
        f.write(f"# Off-Page SEO Backlink Report: {domain}\n")
        f.write(f"**Date:** {today}\n\n")
        f.write("\n\n".join(full_report))

    print(f"\nReport saved to: {report_filename}")
    return report_filename


if __name__ == "__main__":
    report_file = run_backlink_agent()
    print(f"\nDone! Report: {report_file}")
