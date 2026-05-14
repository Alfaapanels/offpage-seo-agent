import anthropic
import json
import os
from datetime import datetime, date
from anthropic import beta_tool
from offpage_seo_agent import (
    analyze_backlink_quality,
    score_link_prospect,
    generate_outreach_template,
    identify_link_gap_opportunity,
)

DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
NICHE = "panels building materials construction"
COMPETITORS = ["solarpanels.com", "alphapanels.com", "paneltech.com", "panelworld.com"]
LOG_FILE = "backlink_log.json"

client = anthropic.Anthropic()


def load_log() -> dict:
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return {"submissions": [], "opportunities": [], "daily_reports": {}}


def save_log(log: dict) -> None:
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2, default=str)


@beta_tool
def log_opportunity(platform: str, url: str, opportunity_type: str, notes: str) -> str:
    """Log a newly discovered backlink opportunity.

    Args:
        platform: Website or platform name.
        url: URL of the page where a backlink can be obtained.
        opportunity_type: One of: guest_post, directory, forum, resource_page, broken_link, mention, web2.
        notes: Key details — contact info, page topic, why it's relevant.
    """
    log = load_log()
    existing_urls = {o["url"] for o in log["opportunities"]}
    if url in existing_urls:
        return f"Already logged: {url}"
    log["opportunities"].append({
        "date": str(date.today()),
        "platform": platform,
        "url": url,
        "type": opportunity_type,
        "notes": notes,
        "status": "pending",
    })
    save_log(log)
    return f"Logged opportunity: {platform} ({opportunity_type}) — {url}"


@beta_tool
def log_submission(
    platform: str,
    url: str,
    submission_type: str,
    anchor_text: str,
    content_summary: str,
) -> str:
    """Log a completed backlink submission or outreach action.

    Args:
        platform: Website where the link was submitted or outreach was sent.
        url: Target URL where the backlink will appear.
        submission_type: One of: directory, forum_post, blog_comment, guest_post_pitch, web2, social, citation.
        anchor_text: Anchor text used or recommended in the outreach.
        content_summary: Brief description of what was submitted or the email sent.
    """
    log = load_log()
    log["submissions"].append({
        "date": str(date.today()),
        "platform": platform,
        "url": url,
        "type": submission_type,
        "anchor_text": anchor_text,
        "content_summary": content_summary,
        "status": "submitted",
    })
    save_log(log)
    return f"Logged submission: {platform} — {submission_type} | anchor: '{anchor_text}'"


@beta_tool
def get_todays_progress() -> str:
    """Return a summary of today's backlink building activity."""
    log = load_log()
    today = str(date.today())
    submissions = [s for s in log["submissions"] if s["date"] == today]
    opportunities = [o for o in log["opportunities"] if o["date"] == today]
    all_time_sub = len(log["submissions"])
    all_time_opp = len(log["opportunities"])
    return (
        f"Progress for {today}:\n"
        f"  New opportunities found: {len(opportunities)}\n"
        f"  Submissions / outreach done: {len(submissions)}\n"
        f"  All-time opportunities logged: {all_time_opp}\n"
        f"  All-time submissions logged: {all_time_sub}\n\n"
        f"Today's submissions:\n{json.dumps(submissions, indent=2)}"
    )


@beta_tool
def get_pending_opportunities(limit: int = 10) -> str:
    """Return pending backlink opportunities not yet actioned.

    Args:
        limit: Maximum number of opportunities to return (default 10).
    """
    log = load_log()
    pending = [o for o in log["opportunities"] if o["status"] == "pending"][:limit]
    if not pending:
        return "No pending opportunities — time to find new ones!"
    return f"Pending opportunities ({len(pending)}):\n{json.dumps(pending, indent=2)}"


@beta_tool
def mark_opportunity_actioned(url: str, result: str) -> str:
    """Mark a logged opportunity with its outcome.

    Args:
        url: URL of the opportunity to update.
        result: One of: submitted, rejected, pending_response, not_suitable.
    """
    log = load_log()
    for opp in log["opportunities"]:
        if opp["url"] == url:
            opp["status"] = result
            opp["actioned_date"] = str(date.today())
            save_log(log)
            return f"Marked {url} as: {result}"
    return f"Opportunity not found: {url}"


@beta_tool
def save_daily_report(report_content: str) -> str:
    """Persist today's backlink building report to disk.

    Args:
        report_content: Full markdown text of the report.
    """
    log = load_log()
    today = str(date.today())
    log["daily_reports"][today] = {
        "content": report_content,
        "generated_at": datetime.now().isoformat(),
    }
    save_log(log)
    report_file = f"backlink_report_{today}.md"
    with open(report_file, "w") as f:
        f.write(f"# Daily Backlink Report — {today}\n\n")
        f.write(f"**Domain:** {DOMAIN}  \n**Brand:** {BRAND_NAME}\n\n")
        f.write(report_content)
    return f"Report saved to {report_file}"


# Each weekday gets a distinct focus so every day covers a different channel.
DAILY_TASKS = {
    0: "Guest Post Outreach — Find 5 authoritative blogs in the construction/panels niche that accept guest posts. Draft a personalised pitch for each.",
    1: "Directory Submissions — Find 10 relevant business directories (niche + local) and submit alfaapanels.com. Log each submission.",
    2: "Forum & Community Engagement — Find 5 active forums or Reddit communities related to panels/construction. Write helpful posts that naturally mention alfaapanels.com with profile or contextual links.",
    3: "Broken Link Building — Search competitor resource pages for broken outbound links. Identify pages on alfaapanels.com that are suitable replacements and draft outreach emails.",
    4: "Resource Page Link Building — Find resource-page compilations ('best panels suppliers', 'top building material sites') and pitch alfaapanels.com for inclusion.",
    5: "Web 2.0 Content Creation — Draft short articles for Medium, Blogger, and Tumblr that link back to alfaapanels.com with keyword-rich anchor text. Log the content and URLs.",
    6: "Citation & Review Sites — Submit alfaapanels.com to Google Business Profile, industry review sites, and local citation platforms. Identify unlinked brand mentions and send conversion emails.",
}


def run_daily_backlink_builder() -> None:
    today = date.today()
    task = DAILY_TASKS[today.weekday()]

    print(f"\nDaily Backlink Builder — {DOMAIN}")
    print(f"Date: {today}  |  Focus: {task[:60]}...")
    print("=" * 70)

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            log_opportunity,
            log_submission,
            get_todays_progress,
            get_pending_opportunities,
            mark_opportunity_actioned,
            save_daily_report,
            analyze_backlink_quality,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are a senior off-page SEO specialist running the daily backlink campaign for {DOMAIN} ({BRAND_NAME}).

Date: {today}
Niche: {NICHE}
Known competitors: {", ".join(COMPETITORS)}

━━━ STEP 1 — SITUATION CHECK ━━━
• Call get_pending_opportunities to see what's already waiting.
• Call get_todays_progress to see if any work was done today already.
• Fetch {DOMAIN} (web_fetch) to understand the product/service so every link you build is genuinely relevant.

━━━ STEP 2 — TODAY'S PRIMARY TASK ━━━
{task}

For every website you find:
  1. Score it with score_link_prospect (use niche = "{NICHE}").
  2. Log it with log_opportunity (include contact email or form URL in notes).
  3. For HIGH/MEDIUM scores, generate the outreach email with generate_outreach_template.
  4. Log the outreach with log_submission, then mark the opportunity with mark_opportunity_actioned.

━━━ STEP 3 — PROCESS PENDING BACKLOG ━━━
Work through up to 5 pending opportunities from get_pending_opportunities that you did not create today. Take action, log it, and mark each as actioned.

━━━ STEP 4 — BRAND MENTION SWEEP ━━━
Search: "{BRAND_NAME}" -site:{DOMAIN}
Find any unlinked mentions and log them as 'mention' opportunities. Draft a polite link-request email for each.

━━━ STEP 5 — COMPETITOR GAP CHECK ━━━
For one competitor, use identify_link_gap_opportunity on 3 different linking-page topics you find via web_search.

━━━ STEP 6 — DAILY REPORT ━━━
Call get_todays_progress, then save a full markdown report via save_daily_report covering:
- Executive summary (what was achieved)
- Top 5 opportunities (URL, type, score, why relevant)
- Ready-to-send outreach emails (full text)
- Recommended actions for tomorrow
- Running totals (all-time opportunities and submissions)

Be specific. Use real URLs. Prioritise relevance to the {NICHE} niche above all else.""",
        }],
    )

    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)


if __name__ == "__main__":
    run_daily_backlink_builder()
