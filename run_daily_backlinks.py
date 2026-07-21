import anthropic
from anthropic import beta_tool
import os
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
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing", "quality", "durable", "innovative"]
    negative_words = ["bad", "worst", "avoid", "scam", "terrible", "poor", "cheap"]
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
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "directory", "supplier", "manufacturer"]
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
        "broken_link": f"Subject: Broken link on your {their_page_topic} page\n\nHi {prospect_name},\n\nI was reading your {their_page_topic} page on {prospect_site} and noticed a broken link.\n\nAlfa Panels has a comprehensive resource at {your_content_url} that would be a great replacement — we specialize in high-quality architectural facade panels and cladding solutions.\n\nWould you consider updating the link?\n\nBest regards,\nAlfa Panels Team\nalfaapanels.com",
        "guest_post": f"Subject: Guest Post Idea for {prospect_site} — Facade Panels & Architectural Cladding\n\nHi {prospect_name},\n\nI've been following your content on {prospect_site}, particularly around {their_page_topic}. Great work!\n\nI'd love to contribute a guest post on behalf of Alfa Panels ({your_site}) — we could write about topics like choosing the right facade panel system, aluminium cladding trends, or sustainable building materials.\n\nWould you be open to a collaboration?\n\nBest regards,\nAlfa Panels Team",
        "resource": f"Subject: Useful resource for your {their_page_topic} page\n\nHi {prospect_name},\n\nYour resource page on {their_page_topic} is excellent! I thought you might want to add Alfa Panels ({your_content_url}) — we manufacture and supply architectural facade panels and aluminium cladding used in commercial and residential construction projects across the region.\n\nIt might be a helpful addition for your readers looking for panel suppliers or building material resources.\n\nWould you take a look?\n\nBest,\nAlfa Panels Team",
        "mention": f"Subject: Thank you for mentioning Alfa Panels!\n\nHi {prospect_name},\n\nThank you for mentioning Alfa Panels in your article about {their_page_topic} on {prospect_site}!\n\nWould you be open to linking directly to {your_content_url}? It would help your readers find us more easily.\n\nThanks again,\nAlfa Panels Team\nalfaapanels.com"
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
    return f"LINK GAP OPPORTUNITY\nCompetitor: {competitor_domain}\nYour site: {your_domain}\nLinking page topic: {linking_page_topic}\n\nActions:\n1. Identify what content earned {competitor_domain} this link\n2. Create better/more comprehensive content on the same topic for {your_domain}\n3. Reach out to the linking page with Alfa Panels' resource\n4. Highlight Alfa Panels' unique value: quality manufacturing, product range, project portfolio"


def run_daily_backlink_session(your_domain: str, brand_name: str, niche: str, competitors: list, today: str):
    print(f"\nDaily Backlink Building Session — {today}")
    print(f"Domain: {your_domain}")
    print("=" * 60)

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-8",
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
            "content": f"""You are an expert off-page SEO strategist. Today's date is {today}.

Perform a complete daily backlink-building session for: {your_domain}

Brand name: {brand_name}
Niche: {niche}
Competitors: {', '.join(competitors)}

Execute these tasks one by one:

TASK 1 — Brand Mention Audit
Search for "{brand_name}" and "Alfa Panels" mentions across the web.
Find unlinked mentions that are link-building opportunities.
Search queries to use:
- "{brand_name}" -site:{your_domain}
- "alfa panels" facade cladding -site:{your_domain}
Use categorize_brand_mention() for each mention found.

TASK 2 — Competitor Backlink Research
For each competitor, search for pages that link to them to find link gap opportunities.
Search queries:
- link:{competitors[0]} facade panels
- "{competitors[0]}" aluminium cladding supplier directory
Use identify_link_gap_opportunity() for the best prospects found.

TASK 3 — Fresh Link Building Opportunities
Find NEW resource pages, industry directories, architectural blogs, and construction forums
that could link to alfaapanels.com. Focus on:
- Architectural facade panel directories
- Construction material supplier listings
- Building industry resource pages
- Aluminium/composite panel blogs and guides
Search queries:
- "aluminium facade panels" site:directory OR site:resources
- "building cladding" supplier directory intitle:resources
- architectural cladding "add your business" OR "submit your site"
- composite panels manufacturer directory construction
Use score_link_prospect() for each opportunity found.

TASK 4 — Today's Outreach Templates
Based on the top 3 prospects found in Task 3, use generate_outreach_template() to create
personalized outreach emails for each.

TASK 5 — Daily Action Plan
Summarize:
- Top 5 specific backlink opportunities discovered today (with URLs and priority)
- 3 ready-to-send outreach emails
- Quick wins (directories/listings where alfaapanels.com can be added immediately)
- Any unlinked brand mentions to convert
Format as a clear action plan the team can execute today."""
        }],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    report_filename = f"reports/backlinks_{today}.md"
    os.makedirs("reports", exist_ok=True)
    with open(report_filename, "w") as f:
        f.write(f"# Daily Backlink Building Report — {today}\n")
        f.write(f"**Domain:** {your_domain}\n\n")
        f.write("\n\n".join(full_report))
    print(f"\nReport saved: {report_filename}")
    return report_filename, full_report


if __name__ == "__main__":
    today = str(date.today())
    report_file, report_content = run_daily_backlink_session(
        your_domain="alfaapanels.com",
        brand_name="Alfa Panels",
        niche="aluminium facade panels architectural cladding composite panels building materials",
        competitors=["alucobond.com", "reynobond.com", "alpolic.com"],
        today=today,
    )
    print(f"\nDone. Report: {report_file}")
