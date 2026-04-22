import anthropic
import schedule
import time
import json
import os
import sys
from datetime import date
from anthropic import beta_tool

client = anthropic.Anthropic()

TARGET_DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
NICHE = "electrical panels solar panels distribution boards switchgear"
COMPETITORS = ["schneider-electric.com", "abb.com", "legrand.com"]
DAILY_TARGET = 5
BACKLINK_LOG_FILE = "backlink_log.json"


def load_backlink_log() -> dict:
    if os.path.exists(BACKLINK_LOG_FILE):
        with open(BACKLINK_LOG_FILE, "r") as f:
            return json.load(f)
    return {"built_links": [], "total": 0, "last_run": None}


def save_backlink_log(log: dict):
    with open(BACKLINK_LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to a URL.

    Args:
        url: Your target URL.
        backlink_url: The URL linking to you.
        anchor_text: The anchor text used in the link.
    """
    quality_signals = []
    generic_anchors = ["click here", "website", "here", "link"]
    if anchor_text.lower() in generic_anchors:
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
    return (
        f"Brand: {brand_name}\nType: {mention_type}\nSentiment: {sentiment}\n"
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
            f"Hi {prospect_name},\n\nI noticed a broken link on your {their_page_topic} page on {prospect_site}.\n\n"
            f"I have a comprehensive guide at {your_content_url} that would be a great replacement.\n\n"
            f"Would you consider updating the link?\n\nBest,\n[Your Name]"
        ),
        "guest_post": (
            f"Subject: Guest Post Idea for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\nI love your content on {prospect_site} about {their_page_topic}.\n\n"
            f"I'd love to contribute a guest post. I write for {your_site}.\n\n"
            f"Would you be open to a collaboration?\n\nBest,\n[Your Name]"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\nYour resource page on {their_page_topic} is great! "
            f"I created {your_content_url} which might help your readers.\n\n"
            f"Would you take a look?\n\nBest,\n[Your Name]"
        ),
        "mention": (
            f"Subject: You mentioned {your_site} - thank you!\n\n"
            f"Hi {prospect_name},\n\nThank you for mentioning {your_site} in your article about {their_page_topic}!\n\n"
            f"Would you be open to linking directly to {your_content_url}?\n\nThanks,\n[Your Name]"
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
        f"LINK GAP OPPORTUNITY\nCompetitor: {competitor_domain}\nYour site: {your_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\nActions:\n"
        f"1. Find what content earned {competitor_domain} this link\n"
        f"2. Create better content on the same topic for {your_domain}\n"
        f"3. Reach out to the linking page with your resource"
    )


@beta_tool
def find_directory_opportunities(niche: str, location: str = "global") -> str:
    """Find relevant web directories to submit your business to.

    Args:
        niche: Your website niche/industry.
        location: Geographic focus (global, US, UK, etc.).
    """
    general_dirs = [
        "manta.com", "yellowpages.com", "yelp.com", "bbb.org",
        "hotfrog.com", "spoke.com", "thomasnet.com", "dnb.com",
        "chamberofcommerce.com", "cylex.us",
    ]
    niche_dirs = [
        "globalspec.com", "engineering360.com", "energycage.com",
        "solarreviews.com", "electricaltechnology.org", "enf-solar.com",
        "solar-directory.com", "greenpages.org", "sunwatts.com",
    ]
    lines = [f"Directory opportunities for '{niche}' ({location}):\n"]
    lines.append("General Business Directories:")
    lines.extend(f"  - {d}" for d in general_dirs[:5])
    lines.append("\nNiche (Electrical/Solar) Directories:")
    lines.extend(f"  - {d}" for d in niche_dirs[:5])
    lines.append("\nSubmission tip: Complete every field, use keyword-rich descriptions.")
    return "\n".join(lines)


@beta_tool
def generate_directory_listing(
    directory_name: str,
    business_name: str,
    website_url: str,
    description: str,
    category: str,
    keywords: str,
) -> str:
    """Generate optimized content for a directory listing submission.

    Args:
        directory_name: Name of the directory site.
        business_name: Your business name.
        website_url: Your website URL.
        description: Business description to optimize.
        category: Business category.
        keywords: Target keywords (comma-separated).
    """
    short_desc = description[:160]
    primary_kw = keywords.split(",")[0].strip()
    full_desc = (
        f"{business_name} is a trusted provider of {primary_kw} for residential and commercial "
        f"applications. We supply high-quality {category.lower()} products including "
        f"{keywords}. Visit {website_url} for product catalogs, technical specs, and quotes."
    )
    return (
        f"DIRECTORY SUBMISSION — {directory_name}\n"
        f"Business Name: {business_name}\n"
        f"URL: {website_url}\n"
        f"Category: {category}\n"
        f"Keywords: {keywords}\n\n"
        f"Short Description (160 chars):\n{short_desc}\n\n"
        f"Full Description:\n{full_desc}\n"
    )


@beta_tool
def find_forum_and_qa_opportunities(niche: str, daily_limit: int = 3) -> str:
    """Find forums, Reddit threads, and Q&A sites to participate in for backlinks.

    Args:
        niche: Your niche/industry keywords.
        daily_limit: Max number of opportunities to return.
    """
    platforms = [
        "Reddit r/solar — solar panel questions",
        "Reddit r/electricians — wiring and panel questions",
        "Reddit r/DIY — home electrical projects",
        "Reddit r/HomeImprovement — panel upgrades",
        "Quora — 'What is the best electrical panel?' threads",
        "Quora — 'How do solar panels work?' threads",
        "DoItYourself.com forums — electrical section",
        "electriciantalk.com — professional forum",
        "contractortalk.com — general contractor forum",
        "Stack Exchange: Home Improvement — panel questions",
    ]
    lines = [f"Q&A and forum opportunities for '{niche}':\n"]
    lines.extend(f"  {i+1}. {p}" for i, p in enumerate(platforms[: daily_limit + 2]))
    lines.append("\nTip: Answer genuinely. Only add your link when it directly helps the reader.")
    return "\n".join(lines)


@beta_tool
def generate_forum_answer(
    question: str,
    platform: str,
    topic: str,
    website_url: str,
    include_link: bool = True,
) -> str:
    """Generate a helpful, natural forum answer with a contextual backlink.

    Args:
        question: The forum question to answer.
        platform: Forum/platform name (e.g., Reddit, Quora).
        topic: The specific topic area (e.g., 'solar panel installation').
        website_url: Your website URL.
        include_link: Whether to include a link in the answer.
    """
    link_line = (
        f"\n\nIf you need more detailed specs or product options, "
        f"{website_url} has comprehensive guides and a full catalog."
        if include_link
        else ""
    )
    return (
        f"FORUM ANSWER — {platform}\n"
        f"Question: {question}\n\n"
        f"Suggested Answer:\n"
        f"Great question about {topic}. Here's what you need to know:\n\n"
        f"[Write 150-250 words covering:\n"
        f"  1. Direct answer to the question\n"
        f"  2. Key technical details relevant to {topic}\n"
        f"  3. Safety or code compliance notes (if electrical)\n"
        f"  4. Professional vs DIY considerations\n"
        f"  5. Cost/efficiency tradeoffs]{link_line}\n"
    )


@beta_tool
def find_guest_post_opportunities(niche: str, domain: str) -> str:
    """Find blogs and sites accepting guest posts in your niche.

    Args:
        niche: Your niche/industry.
        domain: Your domain for context.
    """
    search_queries = [
        f'"{niche}" "write for us"',
        f'"{niche}" "guest post guidelines"',
        f'"{niche}" "submit an article"',
        '"electrical panels" OR "solar panels" "contribute"',
        '"home improvement" "write for us"',
        '"renewable energy" "guest post"',
        '"electrician" "blog" "write for us"',
    ]
    lines = [f"Guest post search queries for '{niche}' (use in Google/Bing):\n"]
    lines.extend(f"  {i+1}. {q}" for i, q in enumerate(search_queries))
    lines.append(f"\nTip: Sort results by date (past year) to find active blogs.")
    return "\n".join(lines)


@beta_tool
def generate_guest_post_pitch(
    blog_name: str,
    blog_url: str,
    editor_name: str,
    proposed_title: str,
    article_outline: str,
    author_bio: str,
    your_site: str,
) -> str:
    """Generate a compelling guest post pitch email.

    Args:
        blog_name: Name of the target blog.
        blog_url: URL of the target blog.
        editor_name: Editor/owner name (use 'there' if unknown).
        proposed_title: Your proposed article title.
        article_outline: Brief 3-5 point outline.
        author_bio: One-sentence author bio.
        your_site: Your website URL.
    """
    return (
        f"Subject: Guest Post Proposal — {proposed_title}\n\n"
        f"Hi {editor_name},\n\n"
        f"I've been reading {blog_name} ({blog_url}) and love how you break down "
        f"complex electrical and solar topics for your audience.\n\n"
        f"I'd like to contribute:\n\n"
        f"**{proposed_title}**\n\n"
        f"Outline:\n{article_outline}\n\n"
        f"About me: {author_bio} I publish at {your_site}.\n\n"
        f"The piece would be 1,200–1,500 words, original, well-researched, and "
        f"exclusive to {blog_name}. Happy to provide writing samples on request.\n\n"
        f"Interested?\n\nBest,\n[Your Name]\n{your_site}\n"
    )


@beta_tool
def track_backlink(
    url_built_on: str,
    link_to: str,
    anchor_text: str,
    link_type: str,
    status: str,
    date_str: str,
    notes: str = "",
) -> str:
    """Record a built or submitted backlink in the tracking log.

    Args:
        url_built_on: URL where the backlink was placed or submitted.
        link_to: Your page being linked to.
        anchor_text: Anchor text used.
        link_type: One of: directory, forum, guest_post, social, resource, mention.
        status: One of: submitted, live, pending, rejected.
        date_str: Date in YYYY-MM-DD format.
        notes: Additional notes.
    """
    log = load_backlink_log()
    entry = {
        "id": len(log["built_links"]) + 1,
        "url_built_on": url_built_on,
        "link_to": link_to,
        "anchor_text": anchor_text,
        "link_type": link_type,
        "status": status,
        "date": date_str,
        "notes": notes,
    }
    log["built_links"].append(entry)
    log["total"] = len(log["built_links"])
    log["last_run"] = date_str
    save_backlink_log(log)
    return f"Tracked #{entry['id']}: {link_type} on {url_built_on} → {link_to} ({status})"


@beta_tool
def get_backlink_stats() -> str:
    """Get current backlink building statistics and progress for alfaapanels.com."""
    log = load_backlink_log()
    if not log["built_links"]:
        return "No backlinks tracked yet. Starting fresh today!"
    by_type: dict = {}
    by_status: dict = {}
    for link in log["built_links"]:
        by_type[link["link_type"]] = by_type.get(link["link_type"], 0) + 1
        by_status[link["status"]] = by_status.get(link["status"], 0) + 1
    lines = [
        f"BACKLINK STATS — {TARGET_DOMAIN}",
        f"Total tracked: {log['total']}",
        f"Last run: {log.get('last_run', 'N/A')}",
        "",
        "By Type:",
    ]
    lines.extend(f"  {k}: {v}" for k, v in by_type.items())
    lines.append("\nBy Status:")
    lines.extend(f"  {k}: {v}" for k, v in by_status.items())
    return "\n".join(lines)


def run_daily_backlink_builder():
    today = date.today().isoformat()
    print(f"\n{'='*60}")
    print(f"  Daily Backlink Builder — {TARGET_DOMAIN}")
    print(f"  Date: {today}")
    print(f"{'='*60}\n")

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            get_backlink_stats,
            find_directory_opportunities,
            generate_directory_listing,
            find_forum_and_qa_opportunities,
            generate_forum_answer,
            find_guest_post_opportunities,
            generate_guest_post_pitch,
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            track_backlink,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[
            {
                "role": "user",
                "content": f"""You are an expert off-page SEO specialist running a daily backlink building session for {TARGET_DOMAIN}.

Today's date: {today}
Target domain: {TARGET_DOMAIN}
Brand: {BRAND_NAME}
Niche: {NICHE}
Competitors: {", ".join(COMPETITORS)}
Daily target: {DAILY_TARGET} backlink opportunities

Execute these tasks in order:

STEP 1 — STATS CHECK
Call get_backlink_stats to review current progress.

STEP 2 — DIRECTORY SUBMISSIONS (2 per day)
- Use web_search to find 2 relevant directories that haven't been used yet
  (search: 'electrical panels supplier directory' or 'solar panels business listing')
- Score each with score_link_prospect
- Generate optimized listing content with generate_directory_listing
- Track each with track_backlink (status: "submitted")

STEP 3 — FORUM & Q&A PARTICIPATION (2 per day)
- Use web_search to find recent questions about electrical panels, solar panels, or distribution boards
  (search: 'electrical panel questions site:reddit.com' or 'solar panel installation quora')
- Find 2 questions where {TARGET_DOMAIN} content would genuinely help
- Generate helpful answers with generate_forum_answer (include link only where natural)
- Track each with track_backlink (status: "pending", type: "forum")

STEP 4 — GUEST POST OUTREACH (1 per day)
- Use web_search to find 1 home improvement, electrical, or solar blog accepting guest posts
  (search: 'electrical blog "write for us"' or 'solar energy blog "guest post"')
- Score the prospect with score_link_prospect
- Generate a pitch with generate_guest_post_pitch
- Track with track_backlink (status: "pending", type: "guest_post")

STEP 5 — BRAND MENTION CHECK
- Search: '"{BRAND_NAME}" -site:{TARGET_DOMAIN}'
- Find 1 unlinked mention and use categorize_brand_mention
- Use generate_outreach_template (type: "mention") to create a conversion email

STEP 6 — DAILY SUMMARY
Print a concise markdown report with:
- Links built/submitted today (with URLs)
- Ready-to-post content (forum answers, pitch emails)
- Running progress total
- Top 3 priority actions for tomorrow

Keep every link relevant and every piece of content genuinely helpful. Quality over quantity.""",
            }
        ],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    report_dir = "daily_reports"
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(report_dir, f"backlinks_{today}.md")
    with open(report_file, "w") as f:
        f.write(f"# Daily Backlink Report: {today}\n")
        f.write(f"**Domain:** {TARGET_DOMAIN}\n\n")
        f.write("\n\n".join(full_report))
    print(f"\nReport saved: {report_file}")


def schedule_daily(run_time: str = "09:00"):
    print(f"Scheduling daily backlink builder at {run_time} for {TARGET_DOMAIN}...")
    run_daily_backlink_builder()  # run immediately on start
    schedule.every().day.at(run_time).do(run_daily_backlink_builder)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    if "--schedule" in sys.argv:
        run_time = "09:00"
        for arg in sys.argv:
            if arg.startswith("--time="):
                run_time = arg.split("=", 1)[1]
        schedule_daily(run_time)
    else:
        run_daily_backlink_builder()
