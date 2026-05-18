import anthropic
import json
import os
import schedule
import time
from datetime import datetime, date
from anthropic import beta_tool

client = anthropic.Anthropic()

# ── Site configuration ────────────────────────────────────────────────────────
SITE_CONFIG = {
    "domain": "alfaapanels.com",
    "brand_name": "Alfa Panels",
    "niche": "SMM panel services, social media marketing, buy followers likes views",
    "competitors": ["smmking.com", "peakerr.com", "justanotherpanel.com", "smmfollows.com"],
    "target_keywords": [
        "SMM panel",
        "cheapest SMM panel",
        "best SMM panel 2025",
        "buy Instagram followers",
        "social media marketing panel",
        "affordable SMM services",
        "reseller SMM panel",
    ],
}

BACKLINKS_LOG = "built_backlinks.json"
REPORTS_DIR = "daily_reports"


# ── Persistence helpers ───────────────────────────────────────────────────────

def load_backlinks_log() -> dict:
    if os.path.exists(BACKLINKS_LOG):
        with open(BACKLINKS_LOG) as f:
            return json.load(f)
    return {"built": [], "attempted": [], "total_count": 0}


def save_backlinks_log(log: dict) -> None:
    with open(BACKLINKS_LOG, "w") as f:
        json.dump(log, f, indent=2)


def already_tracked(url: str, log: dict) -> bool:
    all_urls = [e["url"] for e in log.get("built", []) + log.get("attempted", [])]
    return url in all_urls


# ── SEO tools ─────────────────────────────────────────────────────────────────

@beta_tool
def track_backlink(url: str, link_type: str, status: str, anchor_text: str, notes: str) -> str:
    """Record a built or attempted backlink in the persistent log.

    Args:
        url: The page URL where the backlink was placed or attempted.
        link_type: Category: 'directory', 'forum', 'qa', 'guest_post', 'resource', 'comment'.
        status: 'built', 'attempted', or 'rejected'.
        anchor_text: Anchor text used for the link.
        notes: Any extra notes about this backlink.
    """
    log = load_backlinks_log()
    if already_tracked(url, log):
        return f"SKIP: {url} already in log — avoiding duplicate."
    entry = {
        "url": url,
        "link_type": link_type,
        "status": status,
        "anchor_text": anchor_text,
        "notes": notes,
        "date": str(date.today()),
    }
    bucket = "built" if status == "built" else "attempted"
    log[bucket].append(entry)
    log["total_count"] = len(log["built"]) + len(log["attempted"])
    save_backlinks_log(log)
    return f"Tracked ({status}): {url} | type={link_type} | anchor='{anchor_text}'"


@beta_tool
def get_backlink_stats() -> str:
    """Return a summary of all backlinks built so far."""
    log = load_backlinks_log()
    built = log.get("built", [])
    attempted = log.get("attempted", [])
    by_type: dict = {}
    for e in built:
        by_type[e["link_type"]] = by_type.get(e["link_type"], 0) + 1
    breakdown = "\n".join(f"  {k}: {v}" for k, v in by_type.items()) or "  none yet"
    return (
        f"Total tracked: {log['total_count']}\n"
        f"Built: {len(built)}\n"
        f"Attempted: {len(attempted)}\n"
        f"Built by type:\n{breakdown}"
    )


@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to a URL.

    Args:
        url: Your target URL.
        backlink_url: The URL linking to you.
        anchor_text: The anchor text used in the link.
    """
    signals = []
    generic = ["click here", "website", "here", "link", "read more"]
    if anchor_text.lower() in generic:
        signals.append("Warning: Generic anchor text — low value")
    else:
        signals.append(f"Good: Descriptive anchor '{anchor_text}'")
    toxic_words = ["spam", "casino", "viagra", "adult", "porn"]
    if any(w in backlink_url.lower() for w in toxic_words):
        signals.append("TOXIC — disavow recommended")
    else:
        signals.append("Domain appears clean")
    authority = [".edu", ".gov", ".org"]
    if any(s in backlink_url for s in authority):
        signals.append("High-authority domain TLD (+bonus)")
    return "\n".join(signals)


@beta_tool
def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    """Categorize a brand mention as linked/unlinked and determine sentiment.

    Args:
        mention_text: The text containing the brand mention.
        brand_name: Your brand or website name.
    """
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive = ["great", "best", "excellent", "recommend", "love", "amazing", "top", "cheap", "affordable"]
    negative = ["bad", "worst", "avoid", "scam", "terrible", "poor", "fake"]
    pos = sum(1 for w in positive if w in mention_text.lower())
    neg = sum(1 for w in negative if w in mention_text.lower())
    sentiment = "Positive" if pos > neg else "Negative" if neg > pos else "Neutral"
    mention_type = "Linked mention" if has_link else "Unlinked mention (link opportunity!)"
    action = "Monitor" if has_link else "Reach out to add your link"
    return f"Brand: {brand_name}\nType: {mention_type}\nSentiment: {sentiment}\nAction: {action}"


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
    content = (page_title + " " + page_content_snippet).lower()
    relevance = sum(1 for w in niche_words if w in content)
    if relevance >= 3:
        score += 40
        reasons.append("High niche relevance (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate niche relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    high_value = ["resource", "guide", "tools", "blog", "list", "best", "top", "review"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value):
        score += 30
        reasons.append("Resource/guide/list page (+30)")
    authority = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority):
        score += 30
        reasons.append("High-authority domain (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Score: {score}/100 — {priority}\nURL: {page_url}\n" + "\n".join(reasons)


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
        link_type: One of 'guest_post', 'broken_link', 'resource', 'mention'.
    """
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\nI found a broken link on your {their_page_topic} page at {prospect_site}.\n\n"
            f"My resource at {your_content_url} would be a perfect replacement.\n\n"
            f"Would you consider updating the link?\n\nBest,\n[Your Name]"
        ),
        "guest_post": (
            f"Subject: Guest Post Idea for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\nI enjoy your content on {their_page_topic} at {prospect_site}.\n\n"
            f"I write for {your_site} and would love to contribute a guest post. "
            f"I can share my expertise on social media marketing and SMM panels.\n\n"
            f"Open to a collaboration?\n\nBest,\n[Your Name]"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\nYour resource page on {their_page_topic} is excellent!\n\n"
            f"I created {your_content_url} which could add real value for your readers.\n\n"
            f"Would you consider adding it?\n\nBest,\n[Your Name]"
        ),
        "mention": (
            f"Subject: You mentioned {your_site} — thank you!\n\n"
            f"Hi {prospect_name},\n\nThank you for mentioning {your_site} in your article on {their_page_topic}!\n\n"
            f"Would you be open to linking directly to {your_content_url}? "
            f"It would help your readers find us easily.\n\nThanks,\n[Your Name]"
        ),
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def identify_link_gap_opportunity(competitor_domain: str, your_domain: str, linking_page_topic: str) -> str:
    """Identify a competitor backlink as an opportunity for your site.

    Args:
        competitor_domain: Competitor's domain.
        your_domain: Your domain.
        linking_page_topic: Topic of the page linking to the competitor.
    """
    return (
        f"LINK GAP OPPORTUNITY\n"
        f"Competitor: {competitor_domain}\n"
        f"Your site: {your_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Action plan:\n"
        f"1. Find the exact page on {competitor_domain} that earned this link\n"
        f"2. Create a better, more comprehensive resource on the same topic for {your_domain}\n"
        f"3. Reach out to the linking site with your superior resource"
    )


@beta_tool
def generate_qa_answer(question: str, platform: str, your_domain: str, keyword: str) -> str:
    """Generate a high-quality Q&A answer with a natural backlink.

    Args:
        question: The question being answered.
        platform: Platform name (e.g. 'Quora', 'Reddit', 'Stack Exchange').
        your_domain: Your website domain to link back to.
        keyword: The primary keyword to optimise the answer for.
    """
    return (
        f"Platform: {platform}\n"
        f"Question: {question}\n\n"
        f"--- ANSWER TEMPLATE ---\n"
        f"Great question! For anyone looking for {keyword}, there are a few things to consider:\n\n"
        f"1. Always choose a provider with a proven track record and transparent pricing.\n"
        f"2. Look for platforms that offer real, high-retention services — not bots.\n"
        f"3. Customer support matters: 24/7 live chat is a must.\n\n"
        f"I've personally had good results with {your_domain} — they offer a wide range of "
        f"services at competitive prices with instant delivery. Worth checking out.\n\n"
        f"Hope that helps!\n"
        f"--- END TEMPLATE ---\n\n"
        f"Note: Customise the answer to sound natural on {platform}. "
        f"Keep the link contextual and only use it if it genuinely adds value."
    )


@beta_tool
def find_directory_submission_targets(niche: str, your_domain: str) -> str:
    """Return a prioritised list of directory types to submit your site to.

    Args:
        niche: Your website's niche/topic.
        your_domain: Your domain.
    """
    directories = [
        ("Google Business Profile", "https://business.google.com", "FREE — highest priority"),
        ("Bing Places for Business", "https://www.bingplaces.com", "FREE — high priority"),
        ("Clutch.co", "https://clutch.co", "Tech/service companies — high DA"),
        ("G2.com", "https://g2.com", "Software/services — high DA"),
        ("Trustpilot", "https://www.trustpilot.com", "Reviews platform — very high DA"),
        ("Sitejabber", "https://www.sitejabber.com", "Consumer reviews — good DA"),
        ("BrightLocal", "https://www.brightlocal.com/free-local-citation-burst", "Local citations"),
        ("AboutUs.org", "https://aboutus.org", "General web directory"),
        ("Jasmine Directory", "https://www.jasminedirectory.com", "Curated web directory"),
        ("Best of the Web", "https://botw.org", "Premium directory — high trust"),
    ]
    lines = [f"Directory targets for {your_domain} ({niche}):\n"]
    for name, url, note in directories:
        lines.append(f"• {name} — {url}\n  {note}")
    lines.append(
        f"\nAction: Submit {your_domain} to each directory. "
        f"Use consistent NAP (Name, Address, Phone). "
        f"Track submissions with track_backlink() after each one."
    )
    return "\n".join(lines)


# ── Daily backlink building runner ────────────────────────────────────────────

def run_daily_backlink_builder():
    domain = SITE_CONFIG["domain"]
    brand = SITE_CONFIG["brand_name"]
    niche = SITE_CONFIG["niche"]
    competitors = SITE_CONFIG["competitors"]
    keywords = SITE_CONFIG["target_keywords"]
    today = str(date.today())

    print(f"\n{'=' * 60}")
    print(f"Daily Backlink Builder — {domain}")
    print(f"Date: {today}")
    print(f"{'=' * 60}\n")

    log = load_backlinks_log()
    print(f"Existing backlinks in log: {log['total_count']}\n")

    os.makedirs(REPORTS_DIR, exist_ok=True)

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            generate_qa_answer,
            find_directory_submission_targets,
            track_backlink,
            get_backlink_stats,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO strategist executing a daily backlink building campaign.

Target site: {domain}
Brand: {brand}
Niche: {niche}
Target keywords: {', '.join(keywords)}
Competitors: {', '.join(competitors)}
Today's date: {today}

IMPORTANT: Before building any backlink, check if you have already tracked it (use get_backlink_stats to review progress). Only pursue NEW opportunities not already in the log.

Execute ALL of the following tasks today:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 1 — DIRECTORY SUBMISSIONS (Target: 3 new directories)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Use find_directory_submission_targets() to get a list of directories.
Search the web to find 3 additional niche-specific directories for "{niche}".
For each directory found, use track_backlink() with status='attempted' to log the submission.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 2 — Q&A BACKLINKS (Target: 3 answers)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Search Quora for questions about: {', '.join(keywords[:3])}
Find 3 open questions where you can provide a valuable answer with a contextual link to {domain}.
Use generate_qa_answer() to craft each answer.
Use track_backlink() with link_type='qa' for each opportunity found.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 3 — FORUM & COMMUNITY PARTICIPATION (Target: 3 posts)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Search Reddit, BlackHatWorld, or niche forums for threads about {niche}.
Find 3 threads where a helpful reply with a link to {domain} would be appropriate.
Use track_backlink() with link_type='forum' for each.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 4 — COMPETITOR BACKLINK GAP (Target: 3 opportunities)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Search for sites linking to competitors: {', '.join(competitors[:2])}
Find 3 pages that link to competitors but NOT to {domain}.
Use identify_link_gap_opportunity() and score_link_prospect() for each.
Use track_backlink() with link_type='resource' for each opportunity.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 5 — BRAND MENTION CONVERSION (Target: 2 unlinked mentions)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Search: "{brand}" -site:{domain}
Find unlinked mentions of {brand} or {domain}.
Use categorize_brand_mention() for each mention.
Generate outreach emails using generate_outreach_template() with link_type='mention'.
Use track_backlink() for each mention found.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 6 — GUEST POST OUTREACH (Target: 2 prospects)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Search for blogs accepting guest posts in the {niche} space.
Find 2 high-quality prospects.
Use score_link_prospect() for each.
Generate outreach emails using generate_outreach_template() with link_type='guest_post'.
Use track_backlink() for each prospect.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINAL SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Call get_backlink_stats() and produce a structured daily report with:
1. What was accomplished today (links built/attempted with URLs)
2. Ready-to-use content (Q&A answers, outreach emails)
3. Tomorrow's priority actions
4. Running total of the backlink campaign

Format the report clearly with sections.""",
        }],
    )

    report_parts = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_parts.append(block.text)

    report_path = os.path.join(REPORTS_DIR, f"backlinks_{today}.md")
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report — {domain}\n")
        f.write(f"**Date:** {today}\n\n")
        f.write("\n\n".join(report_parts))

    print(f"\nReport saved: {report_path}")
    updated_log = load_backlinks_log()
    print(f"Total backlinks tracked: {updated_log['total_count']}")


# ── Scheduling ────────────────────────────────────────────────────────────────

def run_scheduler():
    """Run the backlink builder once immediately, then every day at 09:00."""
    print("Starting daily backlink builder for alfaapanels.com...")
    run_daily_backlink_builder()

    schedule.every().day.at("09:00").do(run_daily_backlink_builder)
    print("\nScheduler active — next run at 09:00 daily. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        run_daily_backlink_builder()
    else:
        run_scheduler()
