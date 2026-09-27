"""Daily backlink builder for alfaapanels.com"""
import anthropic
from anthropic import beta_tool
from datetime import date
import os

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
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing"]
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
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best"]
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
        "guest_post": f"Subject: Guest Post Idea for {prospect_site}\n\nHi {prospect_name},\n\nI love your content on {prospect_site} about {their_page_topic}.\n\nI'd love to contribute a guest post. I write for {your_site} (alfaapanels.com), a leading solar panel and cladding solutions provider.\n\nWould you be open to a collaboration?\n\nBest,\nAlfa Panels Team",
        "resource": f"Subject: Resource suggestion for your {their_page_topic} page\n\nHi {prospect_name},\n\nYour resource page on {their_page_topic} is great! I created {your_content_url} which might help your readers interested in solar panels and cladding solutions.\n\nWould you take a look?\n\nBest,\nAlfa Panels Team",
        "mention": f"Subject: You mentioned {your_site} - thank you!\n\nHi {prospect_name},\n\nThank you for mentioning {your_site} in your article about {their_page_topic}!\n\nWould you be open to linking directly to {your_content_url}?\n\nThanks,\nAlfa Panels Team"
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


def run_daily_backlinks():
    today = date.today().isoformat()
    domain = "alfaapanels.com"
    brand = "Alfa Panels"
    niche = "solar panels cladding facade construction building materials"
    competitors = [
        "kingspanpanels.com",
        "metecno.com",
        "rockwool.com"
    ]

    print(f"\n{'='*60}")
    print(f"Daily Backlink Builder - {today}")
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
            "content": f"""You are an expert off-page SEO and link-building specialist working for {domain}.

Today's date: {today}
Target domain: {domain}
Brand name: {brand}
Niche: {niche}
Competitors: {', '.join(competitors)}

Alfaapanels.com sells solar panels, insulated cladding panels, facade systems, and building envelope solutions. Customers are architects, construction companies, and building contractors.

Execute today's link-building session:

TASK 1 - Brand Mention Discovery
Search for "{brand}" OR "alfa panels" mentions online. Use web_search to find:
- Unlinked brand mentions (outreach opportunities)
- Forums, blogs, or news articles discussing the brand
Score each mention using categorize_brand_mention.

TASK 2 - Fresh Link Prospects (use web_search for each)
Find 5+ high-quality link prospects by searching:
a) "solar panel resources" OR "cladding guide" site:.edu OR site:.gov
b) "best solar panels for buildings" intitle:resources
c) "building envelope solutions" blog write-for-us
d) Construction and architecture blogs accepting guest posts
e) Broken links on solar energy resource pages

Score each prospect with score_link_prospect.

TASK 3 - Competitor Gap Analysis
For each competitor, use web_search to find sites linking to them:
- Search: link:{competitors[0]} solar panels
- Search: "{competitors[1]}" site:architecture OR construction blog
Identify top 3 link gaps using identify_link_gap_opportunity.

TASK 4 - Generate Outreach Templates
For the top 3 prospects found today, generate personalized outreach emails using generate_outreach_template.

TASK 5 - Daily Action Report
Summarize:
1. Total prospects found today: X
2. Top 3 HIGH PRIORITY targets (with URLs and contact strategy)
3. Brand mentions requiring follow-up
4. Link gap opportunities vs competitors
5. Specific outreach emails ready to send today
6. Cumulative link-building actions for this week

Format as a clear, actionable daily report."""
        }],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    # Save daily report
    os.makedirs("reports", exist_ok=True)
    report_path = f"reports/backlinks_{today}.md"
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report: {domain}\n")
        f.write(f"**Date:** {today}\n\n")
        f.write("\n\n".join(full_report))

    print(f"\nReport saved to: {report_path}")
    return report_path, full_report


if __name__ == "__main__":
    run_daily_backlinks()
