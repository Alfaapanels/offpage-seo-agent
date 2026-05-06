import anthropic
import json
import os
from datetime import date, datetime
from anthropic import beta_tool

DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfaapanels"
NICHE = "web hosting control panels reseller hosting cPanel WHM"
COMPETITORS = ["cpanel.net", "plesk.com", "directadmin.com", "froxlor.org", "ispconfig.org"]

ACTIVITY_LOG_FILE = "backlink_activity_log.json"

DAILY_TACTICS = {
    0: "forum_participation",
    1: "qa_opportunities",
    2: "directory_submissions",
    3: "guest_post_prospects",
    4: "broken_link_building",
    5: "resource_page_links",
    6: "competitor_gap_analysis",
}

TACTIC_INSTRUCTIONS = {
    "forum_participation": """
Focus on FORUM PARTICIPATION today:
1. Search for active discussions on WebHostingTalk, HostingDiscussion, and tech forums about cPanel, WHM, reseller hosting, control panels
2. Find threads where alfaapanels.com can add genuine value
3. For each relevant thread, note the URL and draft a helpful reply that naturally mentions alfaapanels.com
4. Log at least 5 forum opportunities with drafted responses""",

    "qa_opportunities": """
Focus on Q&A OPPORTUNITIES today:
1. Search Quora for questions about web hosting control panels, cPanel alternatives, reseller hosting setup, WHM configuration
2. Search Reddit (r/webhosting, r/selfhosted, r/sysadmin) for relevant questions
3. For each question, draft a complete, helpful answer that genuinely addresses it and mentions alfaapanels.com where relevant
4. Log at least 5 Q&A opportunities with full drafted answers""",

    "directory_submissions": """
Focus on DIRECTORY SUBMISSIONS today:
1. Find web hosting directories, software directories, and SaaS listings where alfaapanels.com should be listed
2. Search: "web hosting software directory", "control panel directory", "reseller hosting tools list"
3. Verify alfaapanels.com is not already listed before flagging for submission
4. Log at least 5 directories with submission details and contact info""",

    "guest_post_prospects": """
Focus on GUEST POST PROSPECTS today:
1. Find web hosting blogs, tech blogs, and webmaster sites that accept guest posts
2. Search: "web hosting write for us", "hosting blog guest post", "cPanel tutorial blog contribute"
3. Evaluate each site for relevance and audience quality
4. Draft a compelling pitch for each prospect with a specific article idea
5. Log at least 5 guest post opportunities with pitches""",

    "broken_link_building": """
Focus on BROKEN LINK BUILDING today:
1. Find resource pages and link lists about web hosting, control panels, server management
2. Search: "best web hosting control panels", "hosting resources links", "cPanel alternatives list"
3. Use web_fetch to check if links on those pages are still live
4. Identify broken/outdated links that alfaapanels.com could replace
5. Log at least 5 broken link opportunities with replacement suggestions""",

    "resource_page_links": """
Focus on RESOURCE PAGE LINKS today:
1. Find "best of" lists, resource pages, and curated lists about web hosting tools
2. Search: "best web hosting panel", "top hosting control panels", "recommended hosting tools"
3. For each resource page that doesn't include alfaapanels.com, prepare a pitch
4. Score each prospect and prioritize high-value opportunities
5. Log at least 5 resource page opportunities""",

    "competitor_gap_analysis": """
Focus on COMPETITOR LINK GAP ANALYSIS today:
1. Search for pages that link to or mention cpanel.net, plesk.com, directadmin.com
2. Find pages that mention competitors but not alfaapanels.com
3. For each gap, prepare a personalized outreach email explaining alfaapanels.com's advantages
4. Identify opportunities where alfaapanels.com offers clear advantages
5. Log at least 5 competitor gap opportunities""",
}

client = anthropic.Anthropic()


def load_activity_log() -> dict:
    if os.path.exists(ACTIVITY_LOG_FILE):
        with open(ACTIVITY_LOG_FILE) as f:
            return json.load(f)
    return {"processed_urls": [], "outreach_queue": [], "completed_activities": []}


def save_activity_log(log: dict) -> None:
    with open(ACTIVITY_LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


activity_log = load_activity_log()


@beta_tool
def log_backlink_activity(
    activity_type: str,
    url: str,
    description: str,
    action_taken: str,
    expected_impact: str,
) -> str:
    """Log a completed backlink building activity to the permanent activity log.

    Args:
        activity_type: Type of activity (forum_post, directory_submission, outreach_sent, etc.)
        url: The URL where the activity was performed or the opportunity was found.
        description: Brief description of what was found or done.
        action_taken: Specific action taken or recommended next step.
        expected_impact: Expected SEO impact of this activity.
    """
    if url in activity_log["processed_urls"]:
        return f"Already processed: {url} — skipping duplicate"

    activity_log["processed_urls"].append(url)
    activity_log["completed_activities"].append({
        "date": str(date.today()),
        "type": activity_type,
        "url": url,
        "description": description,
        "action_taken": action_taken,
        "expected_impact": expected_impact,
        "timestamp": datetime.now().isoformat(),
    })
    save_activity_log(activity_log)
    return f"Logged: {activity_type} for {url}"


@beta_tool
def check_url_processed(url: str) -> str:
    """Check if a URL has already been processed in a previous session.

    Args:
        url: The URL to check against the activity log.
    """
    if url in activity_log["processed_urls"]:
        return f"ALREADY PROCESSED: {url} — skip this URL"
    return f"NEW URL: {url} — safe to process"


@beta_tool
def add_to_outreach_queue(
    contact_name: str,
    website: str,
    email_hint: str,
    outreach_type: str,
    personalization_notes: str,
    email_template: str,
) -> str:
    """Add a qualified prospect to the outreach queue for follow-up email sending.

    Args:
        contact_name: Name of the site owner or editor.
        website: Their website URL.
        email_hint: Email address or URL of their contact page.
        outreach_type: Type: guest_post, broken_link, resource, mention, directory.
        personalization_notes: Key facts that make this outreach personalized.
        email_template: The full personalized outreach email ready to send.
    """
    existing = [p for p in activity_log["outreach_queue"] if p["website"] == website]
    if existing:
        return f"Already in outreach queue: {website}"

    activity_log["outreach_queue"].append({
        "date_added": str(date.today()),
        "contact_name": contact_name,
        "website": website,
        "email_hint": email_hint,
        "outreach_type": outreach_type,
        "personalization_notes": personalization_notes,
        "email_template": email_template,
        "status": "pending",
    })
    save_activity_log(activity_log)
    return f"Added to outreach queue: {website} ({outreach_type})"


@beta_tool
def get_today_stats() -> str:
    """Get today's backlink building statistics and a summary of all pending outreach."""
    today = str(date.today())
    today_activities = [a for a in activity_log["completed_activities"] if a["date"] == today]
    pending_outreach = [p for p in activity_log["outreach_queue"] if p["status"] == "pending"]

    return (
        f"Stats for {today}:\n"
        f"  Activities completed today: {len(today_activities)}\n"
        f"  Total URLs processed (all time): {len(activity_log['processed_urls'])}\n"
        f"  Pending outreach emails: {len(pending_outreach)}\n\n"
        f"Today's activities:\n{json.dumps(today_activities, indent=2)}"
    )


@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate the quality of a potential backlink opportunity for alfaapanels.com.

    Args:
        url: Your target URL on alfaapanels.com that would receive the link.
        backlink_url: The URL of the page that would link to you.
        anchor_text: The proposed anchor text for the link.
    """
    signals = []

    generic = ["click here", "website", "here", "link", "this", "page", "read more"]
    niche_keywords = ["panel", "hosting", "cpanel", "whm", "reseller", "control panel", "server"]

    if anchor_text.lower() in generic:
        signals.append("Warning: Generic anchor text — low SEO value")
    elif any(kw in anchor_text.lower() for kw in niche_keywords):
        signals.append(f"Excellent: Keyword-rich anchor text '{anchor_text}'")
    else:
        signals.append(f"Good: Descriptive anchor text '{anchor_text}'")

    toxic = ["spam", "casino", "viagra", "porn", "adult", "pills", "lottery"]
    if any(w in backlink_url.lower() for w in toxic):
        signals.append("TOXIC — avoid this link source")
    else:
        signals.append("Domain appears clean")

    if any(s in backlink_url for s in [".edu", ".gov", ".org"]):
        signals.append("High-authority domain type")

    hosting_related = ["hosting", "server", "domain", "cpanel", "whm", "panel", "tech", "web"]
    if any(w in backlink_url.lower() for w in hosting_related):
        signals.append("Relevant to hosting niche — high contextual value")

    return "\n".join(f"  • {s}" for s in signals)


@beta_tool
def score_link_prospect(
    page_url: str, page_title: str, page_content_snippet: str
) -> str:
    """Score a potential link building prospect's relevance and value for alfaapanels.com.

    Args:
        page_url: URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: Short snippet of the page content.
    """
    score = 0
    reasons = []

    hosting_keywords = [
        "hosting", "server", "cpanel", "whm", "panel", "domain", "reseller",
        "vps", "dedicated", "managed", "cloud hosting", "web host", "control panel",
    ]
    content = (page_title + " " + page_content_snippet + " " + page_url).lower()
    matched = sum(1 for kw in hosting_keywords if kw in content)

    if matched >= 4:
        score += 40
        reasons.append(f"Very high hosting relevance ({matched} keywords) (+40)")
    elif matched >= 2:
        score += 25
        reasons.append(f"Good hosting relevance ({matched} keywords) (+25)")
    elif matched >= 1:
        score += 10
        reasons.append(f"Some relevance ({matched} keyword) (+10)")
    else:
        reasons.append("Low relevance (0)")

    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "top",
                        "comparison", "review", "recommended", "directory", "roundup"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/guide/list page — excellent placement (+30)")

    if any(s in page_url for s in [".edu", ".gov", ".org"]):
        score += 30
        reasons.append("High-authority domain type (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")

    priority = "HIGH PRIORITY" if score >= 70 else "MEDIUM PRIORITY" if score >= 40 else "LOW PRIORITY"
    return f"Score: {score}/100 — {priority}\nURL: {page_url}\n" + "\n".join(f"  • {r}" for r in reasons)


@beta_tool
def generate_outreach_email(
    prospect_name: str,
    prospect_site: str,
    their_content_topic: str,
    link_opportunity_type: str,
    specific_page_url: str,
    your_relevant_page: str,
) -> str:
    """Generate a personalized outreach email for alfaapanels.com link building.

    Args:
        prospect_name: Name of the website owner or editor.
        prospect_site: Their website name or domain.
        their_content_topic: Topic of the page where you want a link.
        link_opportunity_type: Type: guest_post, broken_link, resource, mention, directory.
        specific_page_url: Their specific page URL that's relevant.
        your_relevant_page: The alfaapanels.com page URL that would be linked.
    """
    templates = {
        "broken_link": f"""Subject: Broken link on your {their_content_topic} page

Hi {prospect_name},

I was reading your article on {their_content_topic} ({specific_page_url}) and noticed a broken link that's returning a 404 error.

I run Alfaapanels.com — a web hosting control panel platform for resellers. We have a resource at {your_relevant_page} that covers the same topic and would be a great replacement for your readers.

Would you be open to updating the link? Happy to share which link it is.

Best,
[Your Name] | Alfaapanels.com""",

        "guest_post": f"""Subject: Guest post pitch for {prospect_site}: Hosting Panel Guide

Hi {prospect_name},

I've been following {prospect_site}'s content on {their_content_topic} — great stuff. I'd love to contribute a guest post for your readers.

I'm on the team at Alfaapanels.com, a web hosting control panel for resellers. I could write about:
• How to choose the right control panel for your hosting business
• Setting up reseller hosting from scratch (cPanel/WHM guide)
• cPanel vs. Plesk vs. custom panels — an honest comparison

Would any of these work for your audience?

Best,
[Your Name] | Alfaapanels.com""",

        "resource": f"""Subject: Addition suggestion for your {their_content_topic} page

Hi {prospect_name},

Your resource page on {their_content_topic} ({specific_page_url}) is one of the best I've found on this topic.

I wanted to suggest adding Alfaapanels.com ({your_relevant_page}) to your list. We provide:
• Web hosting control panel solutions for resellers
• Easy cPanel/WHM integration
• Comprehensive reseller management tools

I think your readers would find it genuinely useful. Would you take a look?

Best,
[Your Name] | Alfaapanels.com""",

        "mention": f"""Subject: Quick note re: your article on {their_content_topic}

Hi {prospect_name},

Great article on {their_content_topic} at {specific_page_url}! I noticed you mention hosting control panels in the piece.

Alfaapanels.com specializes exactly in this space. Would you consider adding a link to {your_relevant_page} for readers who want to explore this further? It would add real value to an already excellent article.

Thanks for considering it!
[Your Name] | Alfaapanels.com""",

        "directory": f"""Subject: Alfaapanels.com listing request — Web Hosting Control Panels

Hi {prospect_name},

I'd like to submit Alfaapanels.com for inclusion in your {their_content_topic} directory.

Name: Alfaapanels
URL: https://alfaapanels.com
Category: Web Hosting / Control Panels / Reseller Hosting
Short description: Web hosting control panel platform for resellers — easy cPanel/WHM integration, automated account management, and full reseller billing support.

Please let me know if you need anything else.

Best,
[Your Name] | Alfaapanels.com""",
    }

    return templates.get(link_opportunity_type, templates["resource"])


def run_daily_backlink_builder() -> str:
    today = date.today()
    tactic_key = DAILY_TACTICS[today.weekday()]

    print(f"\n{'='*60}")
    print(f"Daily Backlink Builder — {today}")
    print(f"Domain: {DOMAIN}")
    print(f"Today's tactic: {tactic_key.replace('_', ' ').title()}")
    print(f"{'='*60}\n")

    system_content = (
        f"You are an expert off-page SEO specialist building high-quality backlinks for {DOMAIN}.\n\n"
        f"ABOUT ALFAAPANELS.COM:\n"
        f"  Domain: {DOMAIN}\n"
        f"  Brand: {BRAND_NAME}\n"
        f"  Niche: Web hosting control panels, reseller hosting management, cPanel/WHM solutions\n"
        f"  Target audience: Web hosting resellers, hosting providers, system administrators\n"
        f"  Key value: Easy-to-use control panel that simplifies reseller hosting management\n\n"
        f"COMPETITORS: {', '.join(COMPETITORS)}\n\n"
        f"RULES:\n"
        f"  1. Use web_search and web_fetch to find REAL, EXISTING opportunities only\n"
        f"  2. Call check_url_processed before working on any URL\n"
        f"  3. Log every opportunity with log_backlink_activity\n"
        f"  4. Add qualified prospects to the outreach queue with add_to_outreach_queue\n"
        f"  5. Quality over quantity — one excellent link beats 100 low-quality ones\n"
        f"  6. All outreach must be genuine and add value to the recipient"
    )

    user_content = (
        f"Today is {today}. {TACTIC_INSTRUCTIONS[tactic_key]}\n\n"
        f"STEPS:\n"
        f"1. Call get_today_stats to see what's already been done\n"
        f"2. Search for real opportunities using web_search\n"
        f"3. For each URL found, call check_url_processed first\n"
        f"4. Fetch the page with web_fetch to verify the opportunity is real\n"
        f"5. Score each opportunity with score_link_prospect\n"
        f"6. Log quality opportunities with log_backlink_activity\n"
        f"7. For top prospects, generate an email with generate_outreach_email and call add_to_outreach_queue\n"
        f"8. End with a clear summary: opportunities found, logged, added to outreach queue\n\n"
        f"Goal: Find and log at least 5 quality backlink opportunities for {DOMAIN}."
    )

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-7",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        tools=[
            log_backlink_activity,
            check_url_processed,
            add_to_outreach_queue,
            get_today_stats,
            analyze_backlink_quality,
            score_link_prospect,
            generate_outreach_email,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        system=system_content,
        messages=[{"role": "user", "content": user_content}],
    )

    daily_report = []
    print("Agent is working...\n")

    for message in runner:
        for block in message.content:
            if hasattr(block, "type") and block.type == "text":
                print(block.text)
                daily_report.append(block.text)

    report_path = f"daily_report_{today}.md"
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report — {today}\n\n")
        f.write(f"**Domain:** {DOMAIN}  \n")
        f.write(f"**Tactic:** {tactic_key.replace('_', ' ').title()}  \n\n")
        f.write("---\n\n")
        f.write("\n\n".join(daily_report))

    print(f"\n{'='*60}")
    print(f"Report saved: {report_path}")
    print(f"Activity log: {ACTIVITY_LOG_FILE}")
    print(f"{'='*60}")

    return report_path


if __name__ == "__main__":
    run_daily_backlink_builder()
