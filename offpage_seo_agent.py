import anthropic
import logging
import os
from datetime import datetime
from anthropic import beta_tool
from apscheduler.schedulers.blocking import BlockingScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("backlink_agent.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

client = anthropic.Anthropic()

# ── Site configuration ────────────────────────────────────────────────────────
DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
NICHE = "aluminum composite panels building facade cladding construction materials"
COMPETITORS = [
    "alucobond.com",
    "reynobond.com",
    "alupanel.com",
    "dibond.com",
]
# ─────────────────────────────────────────────────────────────────────────────


@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to a URL.

    Args:
        url: Your target URL.
        backlink_url: The URL linking to you.
        anchor_text: The anchor text used in the link.
    """
    quality_signals = []
    generic_anchors = ["click here", "website", "here", "link", "read more"]
    if anchor_text.lower() in generic_anchors:
        quality_signals.append("Warning: Generic anchor text - low value")
    else:
        quality_signals.append(f"Good: Descriptive anchor: '{anchor_text}'")
    if any(word in backlink_url.lower() for word in ["spam", "casino", "viagra", "porn"]):
        quality_signals.append("TOXIC link - disavow recommended")
    else:
        quality_signals.append("Domain appears clean")
    return "\n".join(quality_signals)


@beta_tool
def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    """Categorize a brand mention as linked/unlinked and detect sentiment.

    Args:
        mention_text: The text containing the brand mention.
        brand_name: Your brand or website name.
    """
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing", "quality", "durable"]
    negative_words = ["bad", "worst", "avoid", "scam", "terrible", "poor", "cheap", "fake"]
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
    """Score a potential link building prospect on a 0-100 scale.

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
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "directory", "suppliers"]
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
        link_type: Type: 'guest_post', 'broken_link', 'resource', 'mention'.
    """
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I noticed a broken link on your {their_page_topic} page on {prospect_site}.\n\n"
            f"I have a comprehensive guide at {your_content_url} that would be a perfect replacement.\n\n"
            f"Would you consider updating the link?\n\nBest,\n[Your Name] | {your_site}"
        ),
        "guest_post": (
            f"Subject: Guest Post Idea for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I love your content on {prospect_site} about {their_page_topic}.\n\n"
            f"I write for {your_site} and would love to contribute a high-quality guest post on "
            f"aluminum composite panels or building facade materials for your audience.\n\n"
            f"Would you be open to a collaboration?\n\nBest,\n[Your Name] | {your_site}"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is really helpful! "
            f"I created {your_content_url} which could add value for your readers.\n\n"
            f"Would you take a look?\n\nBest,\n[Your Name] | {your_site}"
        ),
        "mention": (
            f"Subject: You mentioned {your_site} - thank you!\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning {your_site} in your article about {their_page_topic}!\n\n"
            f"Would you be open to linking directly to {your_content_url} so your readers "
            f"can find us easily?\n\nThanks,\n[Your Name] | {your_site}"
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
        f"2. Create better or more detailed content on the same topic for {your_domain}\n"
        f"3. Reach out to the linking page with your superior resource"
    )


@beta_tool
def find_submission_opportunity(platform_type: str, your_domain: str, your_niche: str) -> str:
    """Find directories, forums, or communities where you can submit your site.

    Args:
        platform_type: Type of platform (directory, forum, Q&A, social, industry_listing).
        your_domain: Your domain to submit.
        your_niche: Your website niche for targeting.
    """
    submissions = {
        "directory": (
            f"Directory submission targets for {your_domain}:\n"
            f"- General: dmoz-style directories, Best of the Web\n"
            f"- Industry: construction material directories, building supplier listings\n"
            f"- Local: Google Business Profile, Bing Places\n"
            f"- B2B: Thomasnet, Kompass, GlobalSpec for {your_niche}\n"
            f"Action: Submit site with consistent NAP (Name, Address, Phone)"
        ),
        "forum": (
            f"Forum engagement opportunities for {your_domain}:\n"
            f"- ArchitectureRevived.com forums\n"
            f"- Builderonline.com community\n"
            f"- Reddit: r/architecture, r/construction, r/DIY\n"
            f"- LinkedIn Groups: Construction Professionals, Architects Network\n"
            f"Action: Answer questions, add value, include link in profile/signature"
        ),
        "Q&A": (
            f"Q&A participation targets for {your_domain}:\n"
            f"- Quora: Answer questions about {your_niche}\n"
            f"- Stack Exchange (Engineering): building materials questions\n"
            f"- Yahoo Answers alternatives\n"
            f"Action: Provide expert answers with link to relevant {your_domain} content"
        ),
        "industry_listing": (
            f"Industry-specific listings for {your_domain}:\n"
            f"- Archiexpo.com (architecture products)\n"
            f"- Materialsearch.com\n"
            f"- SpecifiedBy.com\n"
            f"- Sweets.construction (construction products)\n"
            f"- BuildingGreen.com\n"
            f"Action: Create detailed product/company profiles with backlinks"
        ),
    }
    return submissions.get(platform_type, submissions["directory"])


def run_offpage_seo_agent():
    today = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"Starting daily backlink building run for {DOMAIN} — {today}")
    print(f"\n{'=' * 60}")
    print(f"  Daily Backlink Building Agent — {DOMAIN}")
    print(f"  Date: {today}")
    print(f"{'=' * 60}\n")

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-8",
        max_tokens=16000,
        tools=[
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            find_submission_opportunity,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[
            {
                "role": "user",
                "content": f"""You are an expert off-page SEO strategist specialising in B2B building materials.

Today's date: {today}
Target site: {DOMAIN}
Brand: {BRAND_NAME}
Niche: {NICHE}
Competitors: {', '.join(COMPETITORS)}

Your goal for TODAY is to identify and action real backlink-building opportunities. Work through every task below:

──────────────────────────────────────────────
TASK 1 — Brand Mention Audit
──────────────────────────────────────────────
Search for unlinked brand mentions:
  • "{BRAND_NAME}" -site:{DOMAIN}
  • "alfa panels" building materials
For each mention, use categorize_brand_mention to classify it and flag outreach opportunities.

──────────────────────────────────────────────
TASK 2 — Competitor Backlink Gap Analysis
──────────────────────────────────────────────
For each competitor in {COMPETITORS}:
  1. Search: link:COMPETITOR OR "COMPETITOR" resources
  2. Identify sites linking to them but not to {DOMAIN}
  3. Use identify_link_gap_opportunity for each gap found

──────────────────────────────────────────────
TASK 3 — Fresh Link-Building Prospects
──────────────────────────────────────────────
Search for high-value link targets using queries like:
  • "aluminum composite panels" + "resources" OR "suppliers" OR "guide"
  • "building facade materials" + "best suppliers" site:.org OR site:.edu
  • "cladding materials" directory OR listing 2024 OR 2025
  • intitle:"resources" "construction materials"
Use score_link_prospect to evaluate each page found (score top 5).

──────────────────────────────────────────────
TASK 4 — Directory & Community Submissions
──────────────────────────────────────────────
Use find_submission_opportunity for: directory, forum, Q&A, industry_listing
List the top 5 specific platforms to submit/engage on TODAY with direct URLs where possible.

──────────────────────────────────────────────
TASK 5 — Outreach Email Templates
──────────────────────────────────────────────
Generate ready-to-send outreach emails for the top 3 prospects found above.
Use generate_outreach_template with appropriate link_type for each.

──────────────────────────────────────────────
TASK 6 — Daily Action Plan
──────────────────────────────────────────────
Produce a numbered checklist of TODAY's specific actions:
  • Exact URLs to submit/contact
  • Emails ready to send
  • Pages to engage on
  • Expected link acquisition timeline
Prioritise by impact (HIGH / MEDIUM / LOW).""",
            }
        ],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    os.makedirs("reports", exist_ok=True)
    report_filename = f"reports/backlink_report_{DOMAIN.replace('.', '_')}_{today}.md"
    with open(report_filename, "w") as f:
        f.write(f"# Daily Backlink Report: {DOMAIN}\n")
        f.write(f"**Date:** {today}\n\n")
        f.write("\n\n".join(full_report))

    logger.info(f"Report saved → {report_filename}")
    print(f"\nReport saved to: {report_filename}\n")


def main():
    # Run immediately on startup, then schedule daily at 08:00 UTC
    logger.info("Agent starting — running initial backlink build immediately")
    run_offpage_seo_agent()

    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(run_offpage_seo_agent, "cron", hour=8, minute=0)
    logger.info("Scheduler active — next run at 08:00 UTC daily. Press Ctrl+C to stop.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Agent stopped.")


if __name__ == "__main__":
    main()
