import anthropic
import datetime
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
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing", "leading", "trusted", "quality", "reliable"]
    negative_words = ["bad", "worst", "avoid", "scam", "terrible", "poor", "defective", "complaint"]
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
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "manufacturer", "supplier", "directory"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/directory/guide page - high link value (+30)")
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
        "broken_link": f"Subject: Broken link on your {their_page_topic} page\n\nHi {prospect_name},\n\nI was reading your excellent article on {their_page_topic} on {prospect_site} and noticed a broken link that might frustrate your readers.\n\nAlfaa Panels has a comprehensive guide at {your_content_url} that would make a perfect replacement — it covers the topic in depth and is regularly updated.\n\nWould you consider updating the link? Happy to help your readers with quality content.\n\nBest regards,\nAlfaa Panels Team\nwww.alfaapanels.com",
        "guest_post": f"Subject: Guest Post Idea for {prospect_site} — Insulated Panels Expert\n\nHi {prospect_name},\n\nI enjoy your content on {prospect_site}, especially around {their_page_topic}.\n\nI'm with Alfaa Panels (alfaapanels.com), India's leading sandwich panel manufacturer with 35+ years of experience. I'd love to contribute a practical guest post on topics like cold room panel selection, energy-saving insulation, or PUF vs PIR panels — content your readers in construction/industrial sectors would find genuinely useful.\n\nWould you be open to a collaboration?\n\nBest regards,\nAlfaa Panels Team",
        "resource": f"Subject: Useful resource for your {their_page_topic} page\n\nHi {prospect_name},\n\nYour resource page on {their_page_topic} is very helpful — I've bookmarked it myself!\n\nI thought you might like to add Alfaa Panels ({your_content_url}) to your list. We're India's only sandwich panel manufacturer present across all four corners of India, with 35+ years of expertise in PUF, PIR, Rockwool, cold room, and clean room panels.\n\nWould you take a look and consider adding us?\n\nBest regards,\nAlfaa Panels Team\nwww.alfaapanels.com",
        "mention": f"Subject: Thank you for mentioning Alfaa Panels!\n\nHi {prospect_name},\n\nThank you for mentioning Alfaa Panels in your article about {their_page_topic} on {prospect_site} — we truly appreciate it!\n\nWould you be open to linking directly to {your_content_url}? It would help your readers find more detailed information and would mean a lot to our team.\n\nThanks again,\nAlfaa Panels Team\nwww.alfaapanels.com"
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
    return f"LINK GAP OPPORTUNITY\nCompetitor: {competitor_domain}\nYour site: {your_domain}\nLinking page topic: {linking_page_topic}\n\nActions:\n1. Find what content earned {competitor_domain} this link\n2. Create better/more comprehensive content on the same topic for {your_domain}\n3. Reach out to the linking page with your superior resource"


def run_offpage_seo_agent(your_domain: str, brand_name: str, niche: str, competitors: list):
    today = datetime.date.today().isoformat()
    print(f"\nStarting Off-Page SEO Agent for: {your_domain} — {today}\n")
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
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO strategist working for Alfaa Panels.

Today's date: {today}
Target domain: {your_domain}
Brand name: {brand_name}
Industry/Niche: {niche}
Competitors: {', '.join(competitors)}

Your goal is to find FRESH, ACTIONABLE backlink opportunities that have not been reported before.
Focus on high-quality, relevant sites in construction, cold storage, industrial buildings, food processing, pharmaceuticals, and related Indian industries.

Execute ALL of these tasks:

TASK 1 — Brand Mention Audit
Search for "{brand_name}" and "Alfaa Panels" mentions online excluding {your_domain}.
Identify unlinked brand mentions that can be converted to backlinks.
Search queries to use:
- "Alfaa Panels" -site:{your_domain}
- "alfaapanels" -site:{your_domain}

TASK 2 — Competitor Backlink Gap Analysis
For each competitor, find sites that link to them but NOT to {your_domain}.
Search: link:{competitors[0]} OR backlinks to {competitors[0]}
Identify the top 5 link gap opportunities with specific URLs and contact info.

TASK 3 — Fresh Link Building Opportunities
Find NEW link opportunities in these categories:
a) Industry directories listing panel/insulation manufacturers in India
b) Construction/industrial resource pages and buying guides
c) Cold storage and food processing industry blogs/associations
d) Guest post opportunities on construction & building materials sites
e) Broken links on competitor-mentioned pages in this niche
Search for: "sandwich panel manufacturers India" directory, "PUF panel suppliers" list, "cold room manufacturers" guide, "insulated panels" resources India

TASK 4 — Outreach Templates
Generate specific, personalized outreach emails for the top 3 prospects found above.
Use the generate_outreach_template tool for each.

TASK 5 — Today's Action Plan
Create a specific, prioritized action plan for TODAY with:
- 3 outreach emails to send (with full email text)
- 2 directories/listings to submit {your_domain} to
- 1 guest post pitch with a specific topic idea
- Any quick wins (unlinked mentions to claim)

Format the final report in clean Markdown."""
        }],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    report_filename = f"seo_report_{your_domain.replace('.', '_')}_{today}.md"
    with open(report_filename, "w") as f:
        f.write(f"# Off-Page SEO Report: {your_domain}\n")
        f.write(f"**Date:** {today}\n\n")
        f.write("\n\n".join(full_report))
    print(f"\nReport saved to: {report_filename}")
    return report_filename


if __name__ == "__main__":
    run_offpage_seo_agent(
        your_domain="alfaapanels.com",
        brand_name="Alfaa Panels",
        niche="sandwich panel manufacturer insulated panels PUF PIR cold room clean room India",
        competitors=[
            "metecno.in",
            "isothermpufpanel.com",
            "koreapuff.com",
            "industrialfoams.com",
        ]
    )
