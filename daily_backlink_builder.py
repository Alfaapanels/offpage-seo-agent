"""
Daily Backlink Builder for alfaapanels.com

Runs every day, rotating through 7 different backlink strategies (one per weekday).
Tracks all opportunities in a JSON log, saves daily markdown reports.

Usage:
    python daily_backlink_builder.py            # Run today's strategy immediately
    python daily_backlink_builder.py --schedule          # Schedule at 09:00 daily
    python daily_backlink_builder.py --schedule 08:30    # Schedule at custom time
"""

import anthropic
from anthropic import beta_tool
import json
import os
import schedule
import sys
import time
from datetime import date, datetime
from pathlib import Path

client = anthropic.Anthropic()

DOMAIN = "alfaapanels.com"
BRAND = "Alfa Panels"
NICHE = "solar panels electrical panels building materials construction"
TRACKER_FILE = "backlink_tracker.json"
REPORTS_DIR = "daily_reports"

# One strategy per weekday — cycles automatically by date
DAILY_STRATEGIES = {
    0: "directory_submissions",    # Monday
    1: "qa_site_opportunities",    # Tuesday
    2: "forum_participation",      # Wednesday
    3: "resource_page_outreach",   # Thursday
    4: "guest_post_outreach",      # Friday
    5: "broken_link_building",     # Saturday
    6: "brand_mention_conversion", # Sunday
}

# ──────────────────────────────────────────────────────────────
# Tracker helpers
# ──────────────────────────────────────────────────────────────

def load_tracker() -> dict:
    if Path(TRACKER_FILE).exists():
        with open(TRACKER_FILE, "r") as f:
            return json.load(f)
    return {"opportunities": {}, "all_urls": [], "total_logged": 0}


def save_tracker(tracker: dict) -> None:
    with open(TRACKER_FILE, "w") as f:
        json.dump(tracker, f, indent=2)


# ──────────────────────────────────────────────────────────────
# Client-side tools (executed by this process)
# ──────────────────────────────────────────────────────────────

@beta_tool
def get_tracked_urls() -> str:
    """Return all URLs already logged in the tracker so we avoid duplicates.

    Returns a JSON array of URL strings.
    """
    tracker = load_tracker()
    return json.dumps(tracker.get("all_urls", []))


@beta_tool
def log_backlink_opportunity(
    url: str,
    opportunity_type: str,
    score: int,
    outreach_content: str,
    notes: str,
) -> str:
    """Log a discovered backlink opportunity to the persistent tracker.

    Args:
        url: Full URL of the prospect page or directory.
        opportunity_type: One of: directory, forum, qa, resource, guest_post, broken_link, mention.
        score: Quality score 0-100 (use score_link_prospect to calculate this).
        outreach_content: The outreach email or submission content to send/post.
        notes: Brief notes on why this is a good opportunity.
    """
    tracker = load_tracker()
    today = str(date.today())

    if url in tracker["all_urls"]:
        return f"SKIP (already tracked): {url}"

    opportunity = {
        "url": url,
        "type": opportunity_type,
        "score": score,
        "outreach_content": outreach_content,
        "notes": notes,
        "date": today,
        "status": "pending",
        "logged_at": datetime.now().isoformat(),
    }

    tracker["opportunities"].setdefault(today, []).append(opportunity)
    tracker["all_urls"].append(url)
    tracker["total_logged"] = tracker.get("total_logged", 0) + 1

    save_tracker(tracker)
    return f"LOGGED: {url} | type={opportunity_type} | score={score}/100"


@beta_tool
def score_link_prospect(
    page_url: str,
    page_title: str,
    page_content_snippet: str,
    niche: str,
) -> str:
    """Score a potential link building prospect on a 0-100 scale.

    Args:
        page_url: Full URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: A short snippet of the page content (first 500 chars is fine).
        niche: Space-separated keywords describing alfaapanels.com niche.
    """
    score = 0
    reasons = []
    niche_words = niche.lower().split()
    content_lower = (page_title + " " + page_content_snippet).lower()

    relevance = sum(1 for word in niche_words if word in content_lower)
    if relevance >= 3:
        score += 40
        reasons.append(f"High niche relevance: {relevance} keyword matches (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append(f"Moderate niche relevance: {relevance} keyword match (+20)")
    else:
        reasons.append("Low niche relevance (+0)")

    high_value_patterns = ["resource", "guide", "tools", "blog", "list", "best", "top", "review"]
    if any(p in page_url.lower() or p in page_title.lower() for p in high_value_patterns):
        score += 30
        reasons.append("Resource/guide/list page — high link value (+30)")

    authority_signals = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority_signals):
        score += 30
        reasons.append("High-authority domain (.edu/.gov/.org) (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")

    priority = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return (
        f"Score: {score}/100 — {priority} PRIORITY\n"
        + "\n".join(f"  • {r}" for r in reasons)
    )


@beta_tool
def generate_outreach_email(
    prospect_name: str,
    prospect_site: str,
    page_topic: str,
    link_type: str,
    your_content_url: str,
) -> str:
    """Generate a personalised outreach email for a link building prospect.

    Args:
        prospect_name: First name (or 'Editor' if unknown) of the site contact.
        prospect_site: Name of the prospect's website.
        page_topic: Topic of the page where the link would appear.
        link_type: One of: guest_post, broken_link, resource, mention, directory.
        your_content_url: The alfaapanels.com URL to be linked.
    """
    base = {
        "broken_link": (
            f"Subject: Broken link on your {page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I was reading your excellent {page_topic} page on {prospect_site} and noticed "
            f"one of the links appears to be broken.\n\n"
            f"I run Alfa Panels ({DOMAIN}), and we have a detailed resource at {your_content_url} "
            f"that covers the same topic — it might make a great replacement.\n\n"
            f"Happy to share more details if that would help. Thanks for your time!\n\n"
            f"Best regards,\n[Your Name]\nAlfa Panels | {DOMAIN}"
        ),
        "guest_post": (
            f"Subject: Guest post pitch for {prospect_site} — panels & solar energy\n\n"
            f"Hi {prospect_name},\n\n"
            f"I love the content you publish on {prospect_site} about {page_topic}. "
            f"I'm reaching out because I'd love to contribute a guest post.\n\n"
            f"I'm from Alfa Panels ({DOMAIN}) and could write a practical, in-depth piece "
            f"on topics like panel selection, installation best practices, or solar energy ROI "
            f"— tailored to your audience.\n\n"
            f"Would you be open to a collaboration? I'm happy to send a few title ideas first.\n\n"
            f"Best,\n[Your Name]\nAlfa Panels | {DOMAIN}"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your {page_topic} resource page on {prospect_site} is one of the best I've found "
            f"on the subject — great curation!\n\n"
            f"I wanted to suggest a resource we've built at Alfa Panels: {your_content_url}. "
            f"It covers [topic] in detail and has been helpful for contractors and homeowners alike.\n\n"
            f"Would you consider adding it if it fits? No worries if not — thanks for the great page!\n\n"
            f"Best,\n[Your Name]\nAlfa Panels | {DOMAIN}"
        ),
        "mention": (
            f"Subject: Thanks for mentioning Alfa Panels!\n\n"
            f"Hi {prospect_name},\n\n"
            f"I came across your article on {prospect_site} about {page_topic} and noticed "
            f"you mentioned Alfa Panels — thank you!\n\n"
            f"I was wondering if you'd be open to linking directly to our site "
            f"({your_content_url}) so your readers can easily find us?\n\n"
            f"Either way, we appreciate the mention. Keep up the great work!\n\n"
            f"Thanks,\n[Your Name]\nAlfa Panels | {DOMAIN}"
        ),
        "directory": (
            f"Subject: Listing request for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I'd like to submit Alfa Panels for inclusion in the {prospect_site} directory.\n\n"
            f"Company: Alfa Panels\nWebsite: https://{DOMAIN}\n"
            f"Category: {page_topic}\n"
            f"Description: Alfa Panels is a leading provider of high-quality solar and electrical panels, "
            f"serving residential and commercial customers with expert installation support.\n\n"
            f"Please let me know if you need anything else for the listing.\n\n"
            f"Best,\n[Your Name]\nAlfa Panels | {DOMAIN}"
        ),
    }
    return base.get(link_type, base["resource"])


# ──────────────────────────────────────────────────────────────
# Strategy prompts
# ──────────────────────────────────────────────────────────────

STRATEGY_PROMPTS = {
    "directory_submissions": """
## TODAY'S STRATEGY: Web Directory Submissions

Find 10+ high-quality directories and business listings relevant to alfaapanels.com.

Steps:
1. Call get_tracked_urls — skip any URL already logged.
2. Search for these directory types:
   - "solar panel company directory submit"
   - "electrical contractor directory listing"
   - "building materials supplier directory"
   - "construction company directory free submission"
   - "renewable energy business directory"
   - "local business directory solar energy"
3. For each directory found:
   a. Fetch the submission page to confirm it accepts listings.
   b. Score with score_link_prospect (niche: "solar panels electrical panels building materials").
   c. Generate submission content with generate_outreach_email (link_type='directory').
   d. Log with log_backlink_opportunity (type='directory').
4. Also find niche-specific directories: trade associations, solar energy organisations, green energy sites.
5. Prioritise directories with domain authority signals (.org, .gov, established industry sites).
6. Target: minimum 10 valid directory opportunities logged.
""",

    "qa_site_opportunities": """
## TODAY'S STRATEGY: Q&A Site Opportunities

Find 10+ questions on Quora, Reddit, and other Q&A platforms where alfaapanels.com adds value.

Steps:
1. Call get_tracked_urls — skip any URL already logged.
2. Search for relevant questions:
   - site:quora.com "solar panels" OR "electrical panels" buying guide
   - site:reddit.com/r/solar OR r/DIY OR r/homeimprovement panels
   - "best solar panel company" question site:*.com
   - "how to choose electrical panels" forum
   - "solar panel installation tips" questions
3. For each Q&A thread:
   a. Fetch it to read the question and top answers.
   b. Score with score_link_prospect.
   c. Draft a helpful, expert answer (outreach_content) that naturally references alfaapanels.com.
   d. Log with log_backlink_opportunity (type='qa').
4. Focus on questions where alfaapanels.com is genuinely the best resource — no spam.
5. Target: 10+ Q&A opportunities with drafted answers.
""",

    "forum_participation": """
## TODAY'S STRATEGY: Forum Participation

Find 10+ active forum threads where alfaapanels.com expertise adds value.

Steps:
1. Call get_tracked_urls — skip any URL already logged.
2. Search for relevant forums and threads:
   - "solar energy forum" active discussion
   - "electrician forum" panel installation questions
   - "contractor forum" building materials panels
   - "home improvement forum" solar panel advice
   - "green energy community" panels discussion
3. For each forum thread:
   a. Fetch it to verify it's active (recent posts) and relevant.
   b. Score with score_link_prospect.
   c. Draft a helpful reply in outreach_content that positions alfaapanels.com as the expert.
   d. Log with log_backlink_opportunity (type='forum').
4. Look for: trade association forums, contractor communities, DIY communities.
5. Note if the forum allows signature links or contextual links in posts.
6. Target: 10+ forum participation opportunities.
""",

    "resource_page_outreach": """
## TODAY'S STRATEGY: Resource Page Link Building

Find 10+ resource pages that should link to alfaapanels.com.

Steps:
1. Call get_tracked_urls — skip any URL already logged.
2. Search for resource pages:
   - intitle:"resources" "solar panels" site:*.org
   - intitle:"links" OR intitle:"resources" "electrical panels" construction
   - "solar energy resources" guide page
   - "recommended suppliers" panels construction
   - ".edu" renewable energy resources
   - ".gov" solar panel resources homeowners
3. For each resource page:
   a. Fetch it to see what it currently links to and confirm it fits.
   b. Score with score_link_prospect.
   c. Generate pitch with generate_outreach_email (link_type='resource').
   d. Log with log_backlink_opportunity (type='resource').
4. Prioritise .edu and .gov pages — these are high-value authority links.
5. Also find: "best solar panel companies" listicles and buying guides.
6. Target: 10+ resource page outreach opportunities.
""",

    "guest_post_outreach": """
## TODAY'S STRATEGY: Guest Post Outreach

Find 10+ websites that accept guest posts where Alfa Panels expertise is valuable.

Steps:
1. Call get_tracked_urls — skip any URL already logged.
2. Search for guest post opportunities:
   - "write for us" solar energy panels
   - "guest post" electrical construction site:*.com
   - "contribute" OR "submit article" renewable energy
   - "accept guest posts" home improvement construction
   - "become a contributor" solar energy blog
3. For each guest post opportunity:
   a. Fetch the submission/guidelines page.
   b. Score with score_link_prospect.
   c. Generate pitch with generate_outreach_email (link_type='guest_post').
   d. Log with log_backlink_opportunity (type='guest_post').
4. Focus on sites about: home improvement, construction, solar energy, electrical work, green living.
5. Note any Domain Authority signals, audience size, or editorial guidelines.
6. Target: 10+ viable guest post opportunities with personalised pitches.
""",

    "broken_link_building": """
## TODAY'S STRATEGY: Broken Link Building

Find pages in the solar/electrical/construction niche with broken links that alfaapanels.com can replace.

Steps:
1. Call get_tracked_urls — skip any URL already logged.
2. Search for resource-heavy pages that may have dead links:
   - "solar panel supplier" OR "panel manufacturer" site:*.org resources
   - "electrical panel guide" site:*.edu resources links
   - "construction materials resources" links page
   - "solar energy companies list" directory page
3. For each page found:
   a. Fetch it and look for outbound links that appear broken (site down, 404, domain expired).
   b. Identify what content the broken link was pointing to.
   c. Determine how alfaapanels.com content could serve as a replacement.
   d. Score with score_link_prospect.
   e. Generate outreach with generate_outreach_email (link_type='broken_link').
   f. Log with log_backlink_opportunity (type='broken_link').
4. Also search for outdated pages linking to defunct panel companies.
5. Target: 10+ broken link opportunities with replacement proposals.
""",

    "brand_mention_conversion": """
## TODAY'S STRATEGY: Brand Mention Conversion

Find online mentions of Alfa Panels / alfaapanels.com that aren't yet linked, and convert them.

Steps:
1. Call get_tracked_urls — skip any URL already logged.
2. Search for unlinked brand mentions:
   - "alfaapanels" -site:alfaapanels.com
   - "alfa panels" -site:alfaapanels.com
   - "alfapanels.com" -site:alfaapanels.com
   - "alfa-panels" site:*.com
3. For each mention found:
   a. Fetch the page to confirm the mention and whether it has a link.
   b. Score with score_link_prospect.
   c. If unlinked: generate outreach with generate_outreach_email (link_type='mention').
   d. Log with log_backlink_opportunity (type='mention').
4. Also search for reviews, comparisons, or buyer guides mentioning panel brands:
   - "solar panel company review" panels
   - "electrical panel brands comparison" 2024 OR 2025
5. Find competitor mentions — sites covering the industry that should also cover Alfa Panels.
6. Target: 10+ mention conversion or new-mention opportunities.
""",
}


# ──────────────────────────────────────────────────────────────
# Daily session runner
# ──────────────────────────────────────────────────────────────

def run_daily_session() -> Path:
    today = date.today()
    weekday = today.weekday()
    strategy_key = DAILY_STRATEGIES[weekday]
    strategy_prompt = STRATEGY_PROMPTS[strategy_key]

    print(f"\n{'='*62}")
    print(f"  Daily Backlink Builder — {DOMAIN}")
    print(f"  Date: {today}  |  Strategy: {strategy_key}")
    print(f"{'='*62}\n")

    Path(REPORTS_DIR).mkdir(exist_ok=True)

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-7",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        tools=[
            get_tracked_urls,
            log_backlink_opportunity,
            score_link_prospect,
            generate_outreach_email,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert SEO backlink specialist working for {DOMAIN} ({BRAND}).

Your job today is to find and log high-quality backlink opportunities for {DOMAIN}.

Business context:
- Domain: {DOMAIN}
- Brand: {BRAND}
- Niche: {NICHE}

ALWAYS start by calling get_tracked_urls to avoid logging duplicate opportunities.

{strategy_prompt}

QUALITY RULES:
• Only log opportunities with a relevance score ≥ 40 (MEDIUM or HIGH priority).
• Every logged opportunity must have a complete outreach_content — a ready-to-send email or post reply.
• Never log the same URL twice. Check get_tracked_urls at the start.
• Prefer sites that are active and maintained (recent content, working links).
• Relevance to panels, solar energy, electrical work, or construction is mandatory.

After completing the research, provide a concise summary:
1. Total new opportunities logged today
2. Breakdown by opportunity type
3. Top 3 highest-scoring prospects with their outreach emails copied in full
4. One recommended action for tomorrow to build on today's work
""",
        }],
    )

    report_sections: list[str] = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_sections.append(block.text)

    # Persist daily report
    tracker = load_tracker()
    today_opps = tracker["opportunities"].get(str(today), [])

    report_path = Path(REPORTS_DIR) / f"report_{today}.md"
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report — {DOMAIN}\n\n")
        f.write(f"**Date:** {today}  \n")
        f.write(f"**Strategy:** {strategy_key}  \n")
        f.write(f"**New opportunities logged:** {len(today_opps)}  \n")
        f.write(f"**Total all-time logged:** {tracker.get('total_logged', 0)}  \n\n")
        f.write("---\n\n## AI Session Output\n\n")
        f.write("\n\n".join(report_sections))
        if today_opps:
            f.write("\n\n---\n\n## Logged Opportunities\n\n")
            for opp in sorted(today_opps, key=lambda o: o["score"], reverse=True):
                f.write(f"### [{opp['score']}/100] {opp['url']}\n")
                f.write(f"- **Type:** {opp['type']}\n")
                f.write(f"- **Status:** {opp['status']}\n")
                f.write(f"- **Notes:** {opp['notes']}\n")
                f.write(f"- **Outreach:**\n\n```\n{opp['outreach_content']}\n```\n\n")

    print(f"\n{'─'*62}")
    print(f"  Report saved : {report_path}")
    print(f"  Logged today : {len(today_opps)} opportunities")
    print(f"  All-time total: {tracker.get('total_logged', 0)}")
    print(f"{'─'*62}\n")
    return report_path


# ──────────────────────────────────────────────────────────────
# Scheduler
# ──────────────────────────────────────────────────────────────

def start_scheduler(run_time: str = "09:00") -> None:
    print(f"Daily Backlink Builder scheduled at {run_time} every day.")
    print(f"Target: {DOMAIN}  |  Press Ctrl+C to stop.\n")

    schedule.every().day.at(run_time).do(run_daily_session)

    # Run immediately on first launch so the user sees output right away
    run_daily_session()

    while True:
        schedule.run_pending()
        time.sleep(60)


# ──────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--schedule" in sys.argv:
        idx = sys.argv.index("--schedule")
        run_time = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "09:00"
        start_scheduler(run_time)
    else:
        run_daily_session()
