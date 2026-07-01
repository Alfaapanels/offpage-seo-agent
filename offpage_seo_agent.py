import anthropic
import datetime
import os
from anthropic import beta_tool

client = anthropic.Anthropic()

# ── Alfaa Panels configuration ─────────────────────────────────────────────
DOMAIN       = "alfaapanels.com"
BRAND_NAME   = "Alfaa Panels"
NICHE        = "sandwich panel manufacturer insulated panels PUF PIR rockwool clean room cold room panels India"
COMPETITORS  = [
    "kingspaninsulatedpanels.com",
    "metecno.in",
    "isopan.com",
    "tatasteelium.com",
]
# ──────────────────────────────────────────────────────────────────────────


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
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing", "trusted", "quality"]
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
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "directory", "supplier"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/guide page - high link value (+30)")
    authority_signals = [".edu", ".gov", ".org", ".in"]
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
        link_type: Type: 'guest_post', 'broken_link', 'resource', 'mention'.
    """
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I noticed a broken link on your {their_page_topic} page on {prospect_site}.\n\n"
            f"I have a comprehensive guide at {your_content_url} that would be a great replacement.\n\n"
            f"Would you consider updating the link?\n\nBest,\n[Your Name] - {your_site}"
        ),
        "guest_post": (
            f"Subject: Guest Post Idea for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I love your content on {prospect_site} about {their_page_topic}.\n\n"
            f"I'd love to contribute a guest post covering insulated panel applications and best practices. "
            f"I write for {your_site}, India's leading sandwich panel manufacturer.\n\n"
            f"Would you be open to a collaboration?\n\nBest,\n[Your Name] - {your_site}"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is very helpful! "
            f"I created {your_content_url} which covers insulated panel solutions and might add value for your readers.\n\n"
            f"Would you take a look?\n\nBest,\n[Your Name] - {your_site}"
        ),
        "mention": (
            f"Subject: You mentioned {your_site} - thank you!\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning {your_site} in your article about {their_page_topic}!\n\n"
            f"Would you be open to linking directly to {your_content_url} so your readers can learn more?\n\n"
            f"Thanks,\n[Your Name] - {your_site}"
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
        f"Competitor: {competitor_domain}\n"
        f"Your site: {your_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Actions:\n"
        f"1. Find what content earned {competitor_domain} this link\n"
        f"2. Create better/more comprehensive content on the same topic for {your_domain}\n"
        f"3. Reach out to the linking page editor with your superior resource"
    )


def run_offpage_seo_agent(
    your_domain: str = DOMAIN,
    brand_name: str = BRAND_NAME,
    niche: str = NICHE,
    competitors: list = None,
):
    if competitors is None:
        competitors = COMPETITORS

    today = datetime.date.today().isoformat()
    print(f"\n{'='*60}")
    print(f"Off-Page SEO Agent — {brand_name}")
    print(f"Run date : {today}")
    print(f"Domain   : {your_domain}")
    print(f"{'='*60}\n")

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
            "content": f"""You are an expert off-page SEO strategist working for {brand_name} ({your_domain}).

{brand_name} is India's leading sandwich panel manufacturer with 35+ years of experience.
Products: PUF panels, PIR panels, Rockwool panels, Clean Room panels, Cold Room panels,
insulated wall & roof panels. Serves industrial, pharmaceutical, food processing, and
cold storage sectors across India. BIS certified, 15-year warranty.

Niche: {niche}
Competitors: {', '.join(competitors)}
Today's date: {today}

Execute ALL five tasks below and use the available tools throughout:

─── TASK 1 — Brand Mention Audit ───────────────────────────────────────────
Search for "{brand_name}" mentions across the web (exclude {your_domain} itself):
  Query: "{brand_name}" -site:{your_domain}
Also try: "Alfaa Panels review", "alfaapanels.com", "alfa panels India insulated"
For each mention found, call categorize_brand_mention to classify it.
List the top 5 unlinked mentions as immediate outreach targets.

─── TASK 2 — Competitor Backlink Gap Analysis ───────────────────────────────
For each competitor, search for sites that link to them but likely not to {your_domain}.
Queries to run:
  link:kingspaninsulatedpanels.com insulated panels India
  "metecno" panels supplier India
  best sandwich panel manufacturers India (look for directories/lists)
Use identify_link_gap_opportunity for each promising gap found.
Goal: find at least 5 domains linking to competitors that we should target.

─── TASK 3 — Link Building Opportunities ────────────────────────────────────
Search for these high-value link types in the panels/construction/insulation niche:
  a) Resource pages: "insulated panels" + "resources" OR "suppliers list" site:.in OR site:.org
  b) Guest post openings: "write for us" + "construction" OR "insulation" OR "cold storage" India
  c) Industry directories: construction material directories India, building materials suppliers India
  d) Broken links: find pages about insulated panels that may have outdated links
  e) Forum/Q&A: look for questions on Quora, Reddit, industry forums about PUF panels, clean rooms
Score each prospect with score_link_prospect. Target at least 8 prospects.

─── TASK 4 — Outreach Email Templates ──────────────────────────────────────
Using the top 3 prospects from Task 3, generate personalised outreach emails
with generate_outreach_template. Use the most appropriate link_type for each.

─── TASK 5 — Final Prioritised Action Plan ──────────────────────────────────
Produce a clear 30-day off-page SEO action plan for {brand_name}:
• Week 1: Quick wins (unlinked mentions, directory submissions)
• Week 2: Outreach (top 5 email campaigns from Tasks 1-3)
• Week 3: Content creation to support link building (what pages to create/improve)
• Week 4: Follow-up & tracking
Include specific anchor text recommendations for each target URL on {your_domain}.
End with KPIs to track monthly progress.""",
        }],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    # Save report with date stamp
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    report_filename = os.path.join(reports_dir, f"seo_report_{today}.md")

    with open(report_filename, "w") as f:
        f.write(f"# Off-Page SEO Report: {brand_name} ({your_domain})\n")
        f.write(f"**Date:** {today}\n\n")
        f.write("\n\n".join(full_report))

    print(f"\nReport saved to: {report_filename}")
    return report_filename


if __name__ == "__main__":
    run_offpage_seo_agent()
