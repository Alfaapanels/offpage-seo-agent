import anthropic
from anthropic import beta_tool
import json
import os
import schedule
import time
from datetime import datetime

TARGET_DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
NICHE = "solar panels energy solutions"
COMPETITORS = ["solaredge.com", "enphase.com", "sunpower.com", "solarworld.com"]
BACKLINKS_LOG = "backlinks_log.json"

client = anthropic.Anthropic()


@beta_tool
def log_backlink_opportunity(
    platform: str,
    submission_url: str,
    anchor_text: str,
    link_type: str,
    content: str,
    status: str,
) -> str:
    """Log a backlink opportunity or submission to track daily progress.

    Args:
        platform: Platform or site name (e.g. 'AllTop Directory', 'Quora', 'Reddit').
        submission_url: URL of the page/form where the backlink was or should be submitted.
        anchor_text: Anchor text to use for the link to alfaapanels.com.
        link_type: Type: 'directory', 'forum', 'social', 'qa', 'blog_comment', 'guest_post', 'resource'.
        content: The content/text submitted or drafted for this backlink.
        status: 'found' | 'submitted' | 'live' | 'pending_approval'.
    """
    log: list = []
    if os.path.exists(BACKLINKS_LOG):
        with open(BACKLINKS_LOG, "r") as f:
            log = json.load(f)

    entry = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "platform": platform,
        "submission_url": submission_url,
        "anchor_text": anchor_text,
        "link_type": link_type,
        "content_preview": content[:200],
        "status": status,
        "target_domain": TARGET_DOMAIN,
    }
    log.append(entry)

    with open(BACKLINKS_LOG, "w") as f:
        json.dump(log, f, indent=2)

    return (
        f"Logged [{link_type}] backlink from '{platform}' -> {TARGET_DOMAIN} "
        f"(anchor: '{anchor_text}', status: {status})"
    )


@beta_tool
def get_backlink_progress() -> str:
    """Return a summary of backlinks built today and total stats for alfaapanels.com."""
    if not os.path.exists(BACKLINKS_LOG):
        return "No backlinks logged yet. Starting fresh today!"

    with open(BACKLINKS_LOG, "r") as f:
        log = json.load(f)

    today = datetime.now().strftime("%Y-%m-%d")
    today_links = [e for e in log if e["date"] == today]

    type_counts: dict = {}
    for entry in log:
        t = entry["link_type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    today_types: dict = {}
    for entry in today_links:
        t = entry["link_type"]
        today_types[t] = today_types.get(t, 0) + 1

    summary = (
        f"Backlink Progress for {TARGET_DOMAIN}\n"
        f"{'=' * 45}\n"
        f"Today ({today}): {len(today_links)} backlinks\n"
        + "\n".join(f"  - {k}: {v}" for k, v in today_types.items())
        + f"\n\nAll-time total: {len(log)} backlinks\n"
        + "\n".join(f"  - {k}: {v}" for k, v in type_counts.items())
    )
    return summary


@beta_tool
def generate_submission_content(content_type: str, topic: str, platform: str) -> str:
    """Generate ready-to-use content for a specific backlink submission type.

    Args:
        content_type: 'directory_description' | 'forum_post' | 'blog_comment' |
                      'social_post' | 'qa_answer' | 'guest_post_pitch'.
        topic: Keyword or topic to focus on (e.g. 'solar panels for home', 'off-grid energy').
        platform: Name of the target platform (e.g. 'DMOZ', 'Reddit r/solar', 'Quora').
    """
    base_url = f"https://{TARGET_DOMAIN}"
    templates = {
        "directory_description": (
            f"Alfa Panels provides high-quality solar panel systems for residential and "
            f"commercial use. Explore our range of photovoltaic solutions, energy storage, "
            f"and off-grid setups at {base_url}. We specialise in {topic}, offering "
            f"competitive pricing, expert consultation, and full installation support."
        ),
        "forum_post": (
            f"I've been researching {topic} extensively and wanted to share a resource "
            f"I found helpful: {base_url}. Alfa Panels covers product specs, efficiency "
            f"comparisons, and installation guides. Worth a look if you're shopping for "
            f"solar solutions on {platform}."
        ),
        "blog_comment": (
            f"Great write-up on {topic}! One resource worth adding to your list is "
            f"{base_url} — Alfa Panels has detailed guides on system sizing, panel "
            f"efficiency ratings, and ROI calculations that complement what you've covered here."
        ),
        "social_post": (
            f"Looking into {topic}? Check out {base_url} for expert solar panel guides, "
            f"product comparisons, and installation tips. #SolarEnergy #SolarPanels "
            f"#RenewableEnergy #AlfaPanels #{topic.replace(' ', '')}"
        ),
        "qa_answer": (
            f"For {topic}, I'd recommend looking at {base_url}. Alfa Panels provides "
            f"comprehensive resources including panel efficiency comparisons, sizing "
            f"calculators, and installation requirements for both residential and commercial "
            f"setups. Their guides are particularly useful for first-time buyers."
        ),
        "guest_post_pitch": (
            f"Subject: Guest Post Proposal — {topic.title()} Guide for {platform}\n\n"
            f"Hi there,\n\nI'm a solar energy writer with expertise in {topic}. "
            f"I'd love to contribute a guest post to {platform} covering practical "
            f"aspects of {topic} that your readers would find valuable.\n\n"
            f"I write for Alfa Panels ({base_url}) and can provide a unique, data-backed "
            f"perspective. Would you be open to reviewing a draft?\n\nBest regards,\nAlfa Panels Team"
        ),
    }
    return templates.get(content_type, templates["directory_description"])


@beta_tool
def score_link_prospect(
    page_url: str, page_title: str, page_content_snippet: str
) -> str:
    """Score a potential link building prospect for alfaapanels.com relevance.

    Args:
        page_url: URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: Short snippet of page content.
    """
    score = 0
    reasons = []
    niche_words = NICHE.lower().split()
    content_lower = (page_title + " " + page_content_snippet + " " + page_url).lower()

    relevance = sum(1 for word in niche_words if word in content_lower)
    if relevance >= 3:
        score += 40
        reasons.append("High niche relevance (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate niche relevance (+20)")
    else:
        reasons.append("Low relevance (0)")

    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "directory"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/guide/directory page (+30)")

    authority_signals = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority_signals):
        score += 30
        reasons.append("High authority domain (.edu/.gov/.org) (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")

    priority = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return (
        f"Prospect Score: {score}/100 [{priority} PRIORITY]\n"
        f"URL: {page_url}\n"
        "Signals:\n" + "\n".join(f"  - {r}" for r in reasons)
    )


@beta_tool
def identify_link_gap(competitor_domain: str, linking_page_topic: str) -> str:
    """Identify a competitor backlink as a gap opportunity for alfaapanels.com.

    Args:
        competitor_domain: Competitor's domain currently receiving the link.
        linking_page_topic: Topic of the page linking to the competitor.
    """
    return (
        f"LINK GAP OPPORTUNITY\n"
        f"Competitor: {competitor_domain} receives a link about '{linking_page_topic}'\n"
        f"Action plan for {TARGET_DOMAIN}:\n"
        f"  1. Identify the exact page on {competitor_domain} earning this link\n"
        f"  2. Create superior content on the same topic at {TARGET_DOMAIN}\n"
        f"  3. Reach out to the linking page with the improved resource\n"
        f"  4. Use anchor text: '{BRAND_NAME}' or '{linking_page_topic} solutions'"
    )


@beta_tool
def analyze_backlink_quality(backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to alfaapanels.com.

    Args:
        backlink_url: The URL linking to alfaapanels.com.
        anchor_text: The anchor text used in the link.
    """
    signals = []
    generic_anchors = ["click here", "website", "here", "link", "this site"]
    if anchor_text.lower() in generic_anchors:
        signals.append("Warning: Generic anchor text — low SEO value")
    else:
        signals.append(f"Good: Descriptive anchor '{anchor_text}'")

    toxic_signals = ["spam", "casino", "viagra", "adult", "pharma", "payday"]
    if any(word in backlink_url.lower() for word in toxic_signals):
        signals.append("TOXIC domain — add to disavow file")
    else:
        signals.append("Domain appears clean")

    relevant_signals = ["solar", "energy", "panel", "green", "renewable", "photovoltaic"]
    if any(s in backlink_url.lower() for s in relevant_signals):
        signals.append("Topically relevant domain — high value")
    else:
        signals.append("Topically unrelated — moderate value")

    return f"Backlink Quality for {TARGET_DOMAIN}:\n" + "\n".join(f"  - {s}" for s in signals)


def run_daily_backlink_agent():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{'=' * 60}")
    print(f"Daily Backlink Builder — {TARGET_DOMAIN}")
    print(f"Date: {today}")
    print(f"{'=' * 60}\n")

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-7",
        max_tokens=16000,
        tools=[
            log_backlink_opportunity,
            get_backlink_progress,
            generate_submission_content,
            score_link_prospect,
            identify_link_gap,
            analyze_backlink_quality,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[
            {
                "role": "user",
                "content": f"""You are an expert off-page SEO specialist building high-quality backlinks every day for {TARGET_DOMAIN} ({BRAND_NAME}).

Today is {today}. Your goal: find and log at least 10 relevant backlink opportunities today.

Target: {TARGET_DOMAIN}
Brand: {BRAND_NAME}
Niche: {NICHE}
Competitors: {", ".join(COMPETITORS)}

STEP 1 — Check today's progress
Call get_backlink_progress to see what's been done so far today.

STEP 2 — Web Directories & Business Listings
Search for: site:dmoz.org OR site:botw.org OR site:jasminedirectory.com "solar panels"
Also search: "submit site" "solar energy directory" 2024
Find 3 relevant directories and log each with generated directory_description content.

STEP 3 — Q&A Backlinks (Quora, Reddit, StackExchange)
Search: site:quora.com "solar panels" OR "solar energy" questions with no accepted answer
Search: site:reddit.com/r/solar OR r/DIYsolar recent posts asking for recommendations
Find 3 threads, generate qa_answer content for each, and log them.

STEP 4 — Blog Comment Opportunities
Search: "solar panels" OR "solar energy" blog "leave a comment" -site:{TARGET_DOMAIN}
Find 2 relevant blog posts with open comment sections.
Generate blog_comment content and log each opportunity.

STEP 5 — Competitor Backlink Gap Analysis
For each competitor in [{", ".join(COMPETITORS[:2])}]:
  Search: link:{competitor} "solar panels" to find who links to them
  Use identify_link_gap for any opportunities found.
  Log the best 2 gap opportunities.

STEP 6 — Guest Post Outreach
Search: "write for us" "solar energy" OR "renewable energy" OR "solar panels"
Find 2 sites accepting guest posts. Generate guest_post_pitch content and log them.

STEP 7 — Final Summary
Call get_backlink_progress again and print a clean daily summary showing:
- Total backlinks logged today
- Breakdown by type
- Top 3 highest-priority opportunities with action steps

Be thorough. Use generate_submission_content to create ready-to-use content for every opportunity found. Log everything with log_backlink_opportunity.""",
            }
        ],
    )

    report_blocks: list = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_blocks.append(block.text)

    report_path = f"seo_report_{today}.md"
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report — {TARGET_DOMAIN}\n")
        f.write(f"**Date:** {today}\n\n")
        f.write("\n\n".join(report_blocks))
    print(f"\nReport saved: {report_path}")


def main():
    # Run immediately on start
    run_daily_backlink_agent()

    # Schedule to run every day at 08:00
    schedule.every().day.at("08:00").do(run_daily_backlink_agent)
    print(f"\nScheduler active — next run at 08:00 daily for {TARGET_DOMAIN}")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
