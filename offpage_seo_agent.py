import anthropic
from anthropic import beta_tool

client = anthropic.Anthropic()

SITE_CONFIG = {
    "domain": "alfaapanels.com",
    "brand_name": "Alfa Panels",
    "niche": "solar panels aluminum panels building facade cladding construction materials",
    "competitors": [
        "alupanels.com",
        "alpolic.com",
        "reynobond.com",
        "alucobond.com",
        "alucoil.com",
    ],
    "target_keywords": [
        "aluminum composite panels",
        "ACP panels",
        "facade cladding",
        "building cladding panels",
        "alucobond alternative",
        "exterior wall panels",
        "aluminum panels manufacturer",
    ],
}


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
    return (
        f"Brand: {brand_name}\n"
        f"Type: {mention_type}\n"
        f"Sentiment: {sentiment}\n"
        f"Action: {'Monitor' if has_link else 'Reach out to add your link'}"
    )


@beta_tool
def score_link_prospect(
    page_url: str, page_title: str, page_content_snippet: str, your_niche: str
) -> str:
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
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "supplier", "manufacturer"]
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
            f"I noticed a broken link on your {their_page_topic} page on {prospect_site}.\n\n"
            f"I have a comprehensive resource at {your_content_url} that would be a great replacement.\n\n"
            f"Would you consider updating the link?\n\nBest,\n[Your Name] | {your_site}"
        ),
        "guest_post": (
            f"Subject: Guest Post Idea for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I love your content on {prospect_site} about {their_page_topic}.\n\n"
            f"I'd love to contribute a guest post on aluminum composite panels / facade cladding. "
            f"I write for {your_site} — a leading ACP panel manufacturer.\n\n"
            f"Would you be open to a collaboration?\n\nBest,\n[Your Name] | {your_site}"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is very comprehensive! "
            f"I created {your_content_url} which covers aluminum composite panels in depth "
            f"and might add value for your readers.\n\n"
            f"Would you take a look?\n\nBest,\n[Your Name] | {your_site}"
        ),
        "mention": (
            f"Subject: You mentioned {your_site} - thank you!\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning {your_site} in your article about {their_page_topic}!\n\n"
            f"Would you be open to linking directly to {your_content_url} so your readers "
            f"can find the resource easily?\n\nThanks,\n[Your Name] | {your_site}"
        ),
        "directory": (
            f"Subject: Listing request for {prospect_site} directory\n\n"
            f"Hi {prospect_name},\n\n"
            f"I'd like to submit {your_site} for inclusion in your {their_page_topic} directory.\n\n"
            f"Alfa Panels is a manufacturer of high-quality aluminum composite panels (ACP) "
            f"and building facade cladding materials.\n\n"
            f"Listing URL: {your_content_url}\n\nThank you,\n[Your Name] | {your_site}"
        ),
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def identify_link_gap_opportunity(
    competitor_domain: str, your_domain: str, linking_page_topic: str
) -> str:
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
        f"2. Create better / more detailed content on the same topic for {your_domain}\n"
        f"3. Reach out to the linking page with your superior resource"
    )


@beta_tool
def find_directory_submission_targets(niche: str, location: str) -> str:
    """Find relevant business directories and industry listings to submit to.

    Args:
        niche: Your business niche/industry.
        location: Your business location or 'global'.
    """
    directories = [
        "Google Business Profile - local citations",
        "Bing Places for Business",
        "Houzz (construction & building materials)",
        "Thomasnet.com (industrial suppliers)",
        "Kompass.com (B2B directory)",
        "Europages.com (European B2B)",
        "Alibaba Supplier directory",
        "Made-in-China.com",
        "GlobalSpec (engineering & construction)",
        "ConstructConnect (construction network)",
        "Arcat.com (building products library)",
        "Sweets.com (building product specs)",
        "Architizer (architecture community)",
        "ArchDaily (architecture media)",
    ]
    return (
        f"DIRECTORY SUBMISSION TARGETS for {niche} ({location}):\n\n"
        + "\n".join(f"- {d}" for d in directories)
        + "\n\nPriority: Submit to all with NAP (Name, Address, Phone) consistency."
    )


def run_offpage_seo_agent(
    your_domain: str = None,
    brand_name: str = None,
    niche: str = None,
    competitors: list = None,
    report_date: str = None,
):
    cfg = SITE_CONFIG
    your_domain = your_domain or cfg["domain"]
    brand_name = brand_name or cfg["brand_name"]
    niche = niche or cfg["niche"]
    competitors = competitors or cfg["competitors"]

    print(f"\nStarting Off-Page SEO Agent for: {your_domain}")
    if report_date:
        print(f"Report Date: {report_date}")
    print("=" * 60)

    keywords_str = ", ".join(cfg["target_keywords"])

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            find_directory_submission_targets,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[
            {
                "role": "user",
                "content": f"""You are an expert off-page SEO strategist building daily backlinks for {your_domain}.

Website: {your_domain}
Brand: {brand_name}
Niche: {niche}
Target keywords: {keywords_str}
Competitors: {', '.join(competitors)}
Date: {report_date or 'today'}

Execute ALL of these tasks and provide detailed, actionable output:

TASK 1 - Brand Mention Audit
Search for "{brand_name}" and "alfaapanels" mentions online. Find unlinked mentions.
Search: "{brand_name}" -site:{your_domain}
Search: "alfaapanels" -site:{your_domain}
For each unlinked mention found, use categorize_brand_mention tool and flag as opportunity.

TASK 2 - Competitor Backlink Gap Analysis
For each competitor ({', '.join(competitors)}), search for sites linking to them.
Search pattern: link:{comp} OR "{comp}" site reviews
Use identify_link_gap_opportunity for each promising finding.

TASK 3 - Resource Page Link Opportunities
Find resource/guide pages in the aluminum panels and construction niche.
Search: "aluminum composite panels" + "resources" OR "useful links" OR "suppliers"
Search: "ACP panels" + "resource page" OR "building materials resources"
Score each with score_link_prospect tool.

TASK 4 - Guest Post & Directory Opportunities
Find blogs and publications accepting guest posts about:
- Building materials / construction
- Architecture & facades
- Aluminum panel cladding
- Sustainable building materials
Search: "aluminum panels" + "write for us" OR "guest post" OR "contribute"
Also use find_directory_submission_targets for business directories.

TASK 5 - Broken Link Building
Find pages about aluminum panels or facade cladding with broken/outdated links.
Search: "aluminum composite panels suppliers" OR "ACP manufacturers list" (look for 404s).

TASK 6 - Outreach Email Templates
Generate personalized outreach templates for the top 5 prospects found.
Use generate_outreach_template for each: guest_post, resource, broken_link, directory, mention types.

TASK 7 - Daily Action Plan
Provide a specific list of 10 backlink-building actions to execute TODAY.
Format as a checklist with exact URLs, contact points, and steps.

FINAL DELIVERABLE:
A comprehensive daily backlink report with:
- Found opportunities (ranked by priority)
- Ready-to-send outreach emails
- Directories to submit to today
- Specific action steps

Be specific and thorough. Include actual URLs found, not placeholders.""",
            }
        ],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    date_suffix = report_date.replace("-", "") if report_date else "latest"
    report_filename = f"reports/seo_report_{date_suffix}.md"

    import os
    os.makedirs("reports", exist_ok=True)

    with open(report_filename, "w") as f:
        f.write(f"# Daily Backlink Report: {your_domain}\n")
        f.write(f"**Date:** {report_date or 'latest'}\n\n")
        f.write("\n\n".join(full_report))

    print(f"\nReport saved to: {report_filename}")
    return report_filename


if __name__ == "__main__":
    from datetime import date
    run_offpage_seo_agent(report_date=str(date.today()))
