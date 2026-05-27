"""
Daily Backlink Builder for alfaapanels.com
Runs every day to discover and pursue relevant backlink opportunities.
"""

import anthropic
import json
import os
import schedule
import time
from datetime import date
from anthropic import beta_tool

TARGET_DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
NICHE = "insulated sandwich panels building materials construction facade panels"
COMPETITORS = [
    "kingspan.com",
    "rockwool.com",
    "isover.com",
    "kingspaninsulation.com",
]
TRACKER_FILE = "backlink_tracker.json"

client = anthropic.Anthropic()


# ── Tools ──────────────────────────────────────────────────────────────────────

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
        reasons.append("High relevance to niche (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "supplier", "manufacturer", "directory"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("High-value page type (+30)")
    authority_signals = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority_signals):
        score += 30
        reasons.append("Authority domain (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Score: {score}/100 [{priority}] | {page_url}\n" + "\n".join(f"  - {r}" for r in reasons)


@beta_tool
def generate_outreach_email(
    prospect_name: str,
    prospect_site: str,
    their_page_topic: str,
    link_type: str,
    your_content_url: str,
) -> str:
    """Generate a personalised outreach email for alfaapanels.com.

    Args:
        prospect_name: Name of the site owner / editor (use 'there' if unknown).
        prospect_site: Their website name or domain.
        their_page_topic: Topic of the page where we want the link.
        link_type: 'guest_post', 'broken_link', 'resource', 'mention', or 'directory'.
        your_content_url: The alfaapanels.com URL to be linked.
    """
    base = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I was reading your {their_page_topic} article on {prospect_site} and noticed a broken link.\n\n"
            f"We have a comprehensive resource on the same topic at {your_content_url} that would serve your readers well.\n\n"
            f"Would you consider updating it?\n\nBest regards,\nAlfa Panels Team | {TARGET_DOMAIN}"
        ),
        "guest_post": (
            f"Subject: Guest Post Proposal for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I enjoy the content on {prospect_site} — especially your coverage of {their_page_topic}.\n\n"
            f"We produce high-quality content about insulated panels, building envelopes, and construction materials at Alfa Panels ({TARGET_DOMAIN}). "
            f"I'd love to contribute a guest post that adds genuine value to your readers.\n\n"
            f"A few topic ideas:\n"
            f"  • How to Choose the Right Sandwich Panel for Your Climate\n"
            f"  • Top 5 Mistakes in Facade Panel Installation (and How to Avoid Them)\n"
            f"  • Energy Efficiency Gains from Insulated Building Panels\n\n"
            f"Would any of these fit your editorial calendar?\n\nBest regards,\nAlfa Panels Team | {TARGET_DOMAIN}"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is really helpful — great curation!\n\n"
            f"We've published a detailed guide at {your_content_url} that covers {their_page_topic} from a practitioner's perspective. "
            f"It might be a useful addition for your readers.\n\n"
            f"Happy to return the favour or share your content with our audience.\n\nBest regards,\nAlfa Panels Team | {TARGET_DOMAIN}"
        ),
        "mention": (
            f"Subject: Thank you for mentioning Alfa Panels!\n\n"
            f"Hi {prospect_name},\n\n"
            f"We noticed you mentioned Alfa Panels in your article about {their_page_topic} on {prospect_site} — thank you!\n\n"
            f"Would you be open to turning that mention into a direct link to {your_content_url}? "
            f"It would make it easier for your readers to find us.\n\nBest regards,\nAlfa Panels Team | {TARGET_DOMAIN}"
        ),
        "directory": (
            f"Subject: Listing request – Alfa Panels\n\n"
            f"Hi {prospect_name},\n\n"
            f"I came across {prospect_site} while researching {their_page_topic} directories and would love to submit Alfa Panels for inclusion.\n\n"
            f"Alfa Panels manufactures and supplies high-performance insulated sandwich panels for facades, roofing, and cold storage. "
            f"Our website: {TARGET_DOMAIN}\n\n"
            f"Could you let me know the submission process?\n\nBest regards,\nAlfa Panels Team | {TARGET_DOMAIN}"
        ),
    }
    return base.get(link_type, base["resource"])


@beta_tool
def log_prospect(url: str, link_type: str, status: str, notes: str) -> str:
    """Save a backlink prospect to today's tracker.

    Args:
        url: Prospect URL.
        link_type: Type of link opportunity.
        status: 'new', 'emailed', 'acquired', or 'rejected'.
        notes: Any notes about the prospect.
    """
    tracker = _load_tracker()
    today = str(date.today())
    if today not in tracker:
        tracker[today] = []
    existing = [p for p in tracker[today] if p["url"] == url]
    if existing:
        existing[0].update({"link_type": link_type, "status": status, "notes": notes})
    else:
        tracker[today].append({"url": url, "link_type": link_type, "status": status, "notes": notes})
    _save_tracker(tracker)
    return f"Logged: {url} [{link_type}] status={status}"


@beta_tool
def get_already_processed_urls() -> str:
    """Return all URLs already logged in the tracker to avoid duplicate outreach."""
    tracker = _load_tracker()
    urls = set()
    for day_entries in tracker.values():
        for entry in day_entries:
            urls.add(entry["url"])
    if not urls:
        return "No URLs logged yet — all prospects are fresh."
    return "Already processed:\n" + "\n".join(sorted(urls))


# ── Tracker helpers ────────────────────────────────────────────────────────────

def _load_tracker() -> dict:
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE) as f:
            return json.load(f)
    return {}


def _save_tracker(data: dict):
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ── Daily run ──────────────────────────────────────────────────────────────────

def run_daily():
    today = str(date.today())
    print(f"\n{'='*60}")
    print(f"Daily Backlink Builder — {today}")
    print(f"Target: {TARGET_DOMAIN}")
    print(f"{'='*60}\n")

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            score_link_prospect,
            generate_outreach_email,
            log_prospect,
            get_already_processed_urls,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert link-building specialist working every day for {TARGET_DOMAIN}.

Today is {today}. Your job is to find and document FRESH, RELEVANT backlink opportunities.

Website: {TARGET_DOMAIN}
Brand: {BRAND_NAME}
Niche: {NICHE}
Competitors: {', '.join(COMPETITORS)}

STEP 1 — Check history
Call get_already_processed_urls() first so you never duplicate outreach.

STEP 2 — Brand mention audit (unlinked mentions)
Search: "{BRAND_NAME}" -site:{TARGET_DOMAIN}
Also search: "alfa panels" building materials
Find any unlinked mentions. For each, call categorize logic and log_prospect with link_type="mention".

STEP 3 — Competitor backlink gap
Pick one competitor from the list. Search:
  link:{COMPETITORS[0]} construction panels
  site:{COMPETITORS[0]} "insulated panels" resource
Find 3 sites that link to them. Score each with score_link_prospect(). Log the best 3.

STEP 4 — Fresh link opportunities (run ALL of these searches today)
a) Resource pages: search  intitle:"resources" "building materials" OR "construction panels" OR "insulated panels"
b) Guest posts: search  "write for us" "construction" OR "building" OR "architecture"
c) Broken links: search  "insulated panels" "sandwich panels" site:.org OR site:.edu
d) Directories: search  "building materials suppliers directory" OR "construction directory submit"
e) Industry blogs: search  "sandwich panel blog" OR "facade panel blog" write for us guest post

STEP 5 — Fetch & score
For each promising URL found, call web_fetch to read the page, then score_link_prospect().
Only log URLs scoring ≥ 40 with log_prospect(). Aim for at least 5 new prospects today.

STEP 6 — Outreach emails
For each HIGH or MEDIUM prospect you logged, call generate_outreach_email() and print the email.

STEP 7 — Daily summary
Print a markdown report with:
- Total new prospects found today
- Breakdown by link_type
- Top 3 priority prospects (score + URL)
- All generated outreach emails ready to send
""",
        }],
    )

    full_report: list[str] = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    report_path = f"backlink_report_{today}.md"
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report — {TARGET_DOMAIN} — {today}\n\n")
        f.write("\n\n".join(full_report))
    print(f"\nReport saved: {report_path}")


# ── Scheduler ──────────────────────────────────────────────────────────────────

def start_scheduler(run_time: str = "08:00"):
    """Start the daily scheduler. run_time in 'HH:MM' 24-hour format."""
    print(f"Scheduler started. Backlink builder will run daily at {run_time}.")
    schedule.every().day.at(run_time).do(run_daily)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        run_time = sys.argv[2] if len(sys.argv) > 2 else "08:00"
        start_scheduler(run_time)
    else:
        run_daily()
