import anthropic
import json
import os
from datetime import datetime
from anthropic import beta_tool

client = anthropic.Anthropic()

# ── alfaapanels.com configuration ──────────────────────────────────────────
DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
NICHE = "SMM panel social media marketing services"
COMPETITORS = [
    "peakerr.com",
    "smmstone.com",
    "justanotherpanel.com",
    "smmraja.com",
    "growr.io",
]
BACKLINK_LOG_FILE = "daily_backlinks_log.json"


# ── Custom tools ────────────────────────────────────────────────────────────

@beta_tool
def log_backlink_built(url: str, link_type: str, anchor_text: str, notes: str) -> str:
    """Log a backlink that has been built or a high-priority prospect to act on.

    Args:
        url: The page URL where the backlink was placed or outreach was sent.
        link_type: Type: 'directory', 'forum', 'q_and_a', 'social_profile',
                   'blog_comment', 'guest_post', 'resource_page', 'outreach'.
        anchor_text: Anchor text used or recommended.
        notes: Context — what action was taken or needs to be taken next.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    entry = {
        "date": today,
        "url": url,
        "link_type": link_type,
        "anchor_text": anchor_text,
        "notes": notes,
        "timestamp": datetime.now().isoformat(),
    }

    log: list = []
    if os.path.exists(BACKLINK_LOG_FILE):
        with open(BACKLINK_LOG_FILE, "r") as f:
            log = json.load(f)

    log.append(entry)

    with open(BACKLINK_LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)

    return f"[LOGGED] {link_type} backlink at {url} | anchor: '{anchor_text}'"


@beta_tool
def get_todays_backlink_summary() -> str:
    """Return today's backlink count and breakdown to avoid duplication."""
    today = datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists(BACKLINK_LOG_FILE):
        return f"No backlinks logged yet for {today}. Daily goal: 10 quality backlinks."

    with open(BACKLINK_LOG_FILE, "r") as f:
        log = json.load(f)

    todays = [e for e in log if e["date"] == today]
    type_counts: dict = {}
    for e in todays:
        type_counts[e["link_type"]] = type_counts.get(e["link_type"], 0) + 1

    lines = [f"Backlinks built today ({today}): {len(todays)}"]
    for t, c in type_counts.items():
        lines.append(f"  {t}: {c}")
    remaining = max(0, 10 - len(todays))
    lines.append(f"Remaining to reach daily goal of 10: {remaining}")
    return "\n".join(lines)


@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to a URL.

    Args:
        url: Target URL being linked to.
        backlink_url: The URL providing the backlink.
        anchor_text: Anchor text of the link.
    """
    signals = []
    generic = ["click here", "website", "here", "link", "this"]
    if anchor_text.lower() in generic:
        signals.append("Warning: Generic anchor text — low SEO value")
    else:
        signals.append(f"Good: Descriptive anchor '{anchor_text}'")

    if any(w in backlink_url.lower() for w in ["spam", "casino", "viagra", "porn"]):
        signals.append("TOXIC — disavow recommended")
    else:
        signals.append("Domain appears clean")

    authority = [".edu", ".gov", ".org"]
    if any(s in backlink_url for s in authority):
        signals.append("High-authority domain type")

    return "\n".join(signals)


@beta_tool
def score_link_prospect(
    page_url: str, page_title: str, page_content_snippet: str, your_niche: str
) -> str:
    """Score a potential link building prospect on a 0-100 scale.

    Args:
        page_url: URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: Short content snippet.
        your_niche: Your website's niche.
    """
    score = 0
    reasons = []
    niche_words = your_niche.lower().split()
    combined = (page_title + " " + page_content_snippet).lower()

    relevance = sum(1 for w in niche_words if w in combined)
    if relevance >= 3:
        score += 40
        reasons.append("High niche relevance (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate niche relevance (+20)")
    else:
        reasons.append("Low niche relevance (+0)")

    high_value = ["resource", "guide", "tools", "blog", "list", "best", "top", "review"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value):
        score += 30
        reasons.append("Resource/guide/list page (+30)")

    if any(s in page_url for s in [".edu", ".gov", ".org"]):
        score += 30
        reasons.append("High-authority domain (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")

    priority = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return (
        f"Score: {score}/100 — {priority} PRIORITY\nURL: {page_url}\n"
        + "\n".join(reasons)
    )


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
        prospect_name: Name of the website owner or editor.
        prospect_site: Their website name.
        their_page_topic: Topic of the page where you want a link.
        your_site: Your website name.
        your_content_url: Your content URL to be linked.
        link_type: 'guest_post', 'broken_link', 'resource', or 'mention'.
    """
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\nI came across a broken link on your "
            f"{their_page_topic} page at {prospect_site}.\n\n"
            f"I have a comprehensive resource at {your_content_url} that would "
            f"be a perfect replacement for your readers.\n\n"
            f"Would you consider updating the link?\n\nBest,\n[Your Name]"
        ),
        "guest_post": (
            f"Subject: Guest Post Collaboration for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\nI love your content on {their_page_topic} "
            f"at {prospect_site}. I write for {your_site} and would love to "
            f"contribute a high-quality guest post to your audience.\n\n"
            f"Would you be open to a collaboration?\n\nBest,\n[Your Name]"
        ),
        "resource": (
            f"Subject: Useful resource for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\nYour resource page on {their_page_topic} "
            f"is excellent! I created {your_content_url} at {your_site} which "
            f"could add real value for your visitors.\n\n"
            f"Would you take a look?\n\nBest,\n[Your Name]"
        ),
        "mention": (
            f"Subject: Thank you for mentioning {your_site}!\n\n"
            f"Hi {prospect_name},\n\nThank you for mentioning {your_site} in "
            f"your article about {their_page_topic}!\n\n"
            f"Would you be open to linking directly to {your_content_url}? "
            f"It would help your readers find the resource easily.\n\n"
            f"Thanks,\n[Your Name]"
        ),
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def identify_link_gap_opportunity(
    competitor_domain: str, your_domain: str, linking_page_topic: str
) -> str:
    """Identify a competitor backlink as a link gap opportunity.

    Args:
        competitor_domain: Competitor's domain.
        your_domain: Your domain.
        linking_page_topic: Topic of the page linking to the competitor.
    """
    return (
        f"LINK GAP OPPORTUNITY\n"
        f"Competitor: {competitor_domain}\nYour site: {your_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Action plan:\n"
        f"1. Find the specific content on {competitor_domain} that earned this link\n"
        f"2. Create superior content on the same topic for {your_domain}\n"
        f"3. Reach out to the linking page and pitch your resource as an upgrade"
    )


# ── Daily backlink building session ─────────────────────────────────────────

def run_daily_backlink_session():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{'='*60}")
    print(f"  Daily Backlink Building — {DOMAIN}")
    print(f"  Date: {today}")
    print(f"{'='*60}\n")

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            log_backlink_built,
            get_todays_backlink_summary,
            analyze_backlink_quality,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO link builder working exclusively for {DOMAIN}.

Domain: {DOMAIN}
Brand: {BRAND_NAME}
Niche: {NICHE}
Competitors: {', '.join(COMPETITORS)}
Today's date: {today}

Your mission today is to BUILD 10 high-quality, relevant backlinks for {DOMAIN}.
Call get_todays_backlink_summary first, then work through all tasks below.

─── TASK 1 — Web Directories & Listings ───────────────────────────────────
Search for authoritative web directories, business directories, and SMM/marketing
tool directories that accept submissions. Find at least 3 that {DOMAIN} is not
yet listed on, verify their quality, and log each as a 'directory' backlink.
Use anchor text variants: "Alfa Panels", "best SMM panel", "cheap SMM panel".

─── TASK 2 — Q&A Platforms (Quora / Reddit) ───────────────────────────────
Search Quora and Reddit for questions about:
  - "best SMM panel"
  - "cheap SMM panel reseller"
  - "where to buy social media services"
  - "SMM panel review"
Find 2 active threads where a genuine, helpful answer mentioning {DOMAIN} would
add value. Log each as a 'q_and_a' backlink with the thread URL and a draft
answer that naturally includes {DOMAIN}.

─── TASK 3 — Competitor Backlink Gap ──────────────────────────────────────
For each competitor in [{', '.join(COMPETITORS)}], search for pages linking to
them that do not link to {DOMAIN}. Score the top opportunities, identify the
best link gap, and log it as an 'outreach' backlink with a ready-to-send
outreach email from generate_outreach_template.

─── TASK 4 — Niche Blog Comments ──────────────────────────────────────────
Find 2 recent (last 30 days) blog posts about SMM panels, social media marketing
tools, or growing social media followers. Verify they allow comments. Log each
as a 'blog_comment' backlink with a draft comment that is genuinely helpful and
naturally references {DOMAIN}.

─── TASK 5 — Resource Pages & Guest Post Outreach ─────────────────────────
Search for resource pages listing SMM tools or marketing services. Score prospects
with score_link_prospect. For any HIGH or MEDIUM priority page, generate an
outreach email and log it as 'resource_page'. Also find 1 marketing or social
media blog that accepts guest posts, log as 'guest_post' with a proposed title.

─── TASK 6 — Brand Mention Conversion ─────────────────────────────────────
Search: "Alfa Panels" -site:{DOMAIN}
Find any unlinked mentions. For each, generate a 'mention' outreach email and
log it as an 'outreach' backlink.

─── TASK 7 — Daily Summary ────────────────────────────────────────────────
Call get_todays_backlink_summary to confirm you hit the daily goal of 10 backlinks.
Provide a final prioritized action list: which 3 logged opportunities should be
acted on TODAY for the fastest link acquisition, and why.
""",
        }],
    )

    report_lines: list[str] = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_lines.append(block.text)

    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"backlinks_{today}.md")
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report — {DOMAIN}\n")
        f.write(f"**Date:** {today}\n\n")
        f.write("\n\n".join(report_lines))

    print(f"\nReport saved: {report_path}")
    return report_path


# ── Scheduler (runs every day at 09:00) ─────────────────────────────────────

def start_scheduler():
    from apscheduler.schedulers.blocking import BlockingScheduler

    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(run_daily_backlink_session, "cron", hour=9, minute=0)
    print(f"Scheduler started — {DOMAIN} backlink session runs daily at 09:00 UTC")
    print("Press Ctrl+C to stop.\n")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\nScheduler stopped.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        # Run as daily scheduler: python offpage_seo_agent.py --schedule
        start_scheduler()
    else:
        # Run a single session immediately
        run_daily_backlink_session()
