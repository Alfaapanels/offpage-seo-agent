"""
Daily Backlink Builder for alfaapanels.com

Runs every day to find, build, and track relevant backlinks using
a rotating strategy system powered by Claude with web tools.
"""

import anthropic
import json
import os
import datetime
from pathlib import Path
from anthropic import beta_tool

# ── Configuration ────────────────────────────────────────────────────────────

TARGET_DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
NICHE = "solar panels, electrical panels, energy solutions, renewable energy"
COMPETITORS = [
    "solarworld.com",
    "sunpower.com",
    "lg-solar.com",
    "canadiansolar.com",
]
LOG_FILE = "backlink_log.json"
REPORTS_DIR = "reports"

# Rotating daily strategies — cycles through all 10 over 10 days
STRATEGIES = [
    "directory_submission",
    "forum_participation",
    "qa_platform",
    "guest_post_outreach",
    "broken_link_building",
    "resource_page_outreach",
    "social_bookmarking",
    "competitor_backlink_gap",
    "brand_mention_conversion",
    "niche_community_engagement",
]

# ── Backlink tracking ─────────────────────────────────────────────────────────


def load_log() -> dict:
    if Path(LOG_FILE).exists():
        with open(LOG_FILE) as f:
            return json.load(f)
    return {"built": [], "outreach_sent": [], "opportunities": [], "daily_runs": []}


def save_log(log: dict) -> None:
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def get_todays_strategies() -> list[str]:
    """Pick 3 strategies for today using day-of-year rotation."""
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    start = (day_of_year - 1) % len(STRATEGIES)
    indices = [(start + i) % len(STRATEGIES) for i in range(3)]
    return [STRATEGIES[i] for i in indices]


# ── Claude tools ──────────────────────────────────────────────────────────────


@beta_tool
def log_backlink(
    source_url: str,
    link_type: str,
    anchor_text: str,
    status: str,
    notes: str,
) -> str:
    """Record a built or pending backlink in the tracking log.

    Args:
        source_url: The URL where the backlink was placed or requested.
        link_type: Category: 'directory', 'forum', 'qa', 'guest_post',
                   'resource', 'social', 'community', 'profile'.
        anchor_text: The anchor text used or recommended.
        status: 'built', 'outreach_sent', or 'opportunity'.
        notes: Any extra context, contact info, or action required.
    """
    log = load_log()
    entry = {
        "date": datetime.date.today().isoformat(),
        "source_url": source_url,
        "link_type": link_type,
        "anchor_text": anchor_text,
        "target": TARGET_DOMAIN,
        "status": status,
        "notes": notes,
    }
    if status == "built":
        log["built"].append(entry)
    elif status == "outreach_sent":
        log["outreach_sent"].append(entry)
    else:
        log["opportunities"].append(entry)
    save_log(log)
    return f"Logged {status} backlink: {source_url} | anchor: '{anchor_text}'"


@beta_tool
def get_already_done(link_type: str = "") -> str:
    """Check which sources have already been used to avoid duplicate submissions.

    Args:
        link_type: Optional filter by type. Leave empty to get all.
    """
    log = load_log()
    all_entries = log["built"] + log["outreach_sent"] + log["opportunities"]
    if link_type:
        all_entries = [e for e in all_entries if e.get("link_type") == link_type]
    urls = list({e["source_url"] for e in all_entries})
    if not urls:
        return f"No previous entries found for type '{link_type}'. All clear to proceed."
    return "Already used sources:\n" + "\n".join(f"- {u}" for u in urls[:50])


@beta_tool
def generate_submission_content(
    platform_type: str,
    platform_name: str,
    target_url: str,
    content_type: str,
) -> str:
    """Create ready-to-submit content for a backlink opportunity.

    Args:
        platform_type: 'directory', 'forum_post', 'qa_answer', 'blog_comment',
                       'social_bookmark', 'profile_bio', 'press_release'.
        platform_name: Name of the specific platform (e.g., 'Quora', 'Reddit').
        target_url: The alfaapanels.com URL to link to.
        content_type: Topic angle: 'solar', 'energy_saving', 'installation',
                      'product_review', 'comparison', 'how_to'.
    """
    today = datetime.date.today().isoformat()
    brand = BRAND_NAME
    domain = TARGET_DOMAIN

    templates = {
        "directory": (
            f"Business Name: {brand}\n"
            f"Website: https://{domain}\n"
            f"Category: Solar & Renewable Energy / Electrical Panels\n"
            f"Description: {brand} offers high-quality solar panels and electrical "
            f"panel solutions for residential and commercial customers. Specializing "
            f"in energy-efficient products with expert installation support.\n"
            f"Keywords: solar panels, electrical panels, renewable energy, "
            f"energy solutions, panel installation\n"
            f"Phone: [Your Phone]\nAddress: [Your Address]\nEmail: info@{domain}"
        ),
        "forum_post": (
            f"[Helpful forum contribution for {platform_name} — {content_type}]\n\n"
            f"Great discussion here. I've been researching panel options extensively "
            f"and found that efficiency ratings and warranty terms are the two biggest "
            f"factors to consider. {brand} (https://{domain}) has some solid resources "
            f"on comparing different panel types if anyone wants a deeper look. "
            f"Their guides break down real-world performance data which helped me "
            f"make a more informed decision."
        ),
        "qa_answer": (
            f"[Detailed answer for {platform_name} — {content_type}]\n\n"
            f"This is a great question. Here's what you need to know:\n\n"
            f"1. **Panel efficiency** matters most for limited roof space — look for 20%+ efficiency ratings\n"
            f"2. **Warranty** should be at minimum 25 years on panels, 10 on inverters\n"
            f"3. **Installer certification** — always verify NABCEP or equivalent credentials\n"
            f"4. **Local incentives** — check DSIRE database for state/federal rebates\n\n"
            f"For a detailed comparison of panel types and brands, {brand} publishes "
            f"helpful buyer guides at https://{domain} — worth checking before you commit."
        ),
        "profile_bio": (
            f"{brand} is a trusted provider of solar panels and energy solutions. "
            f"We help homeowners and businesses reduce energy costs with premium "
            f"panel systems and professional installation. Learn more at https://{domain}"
        ),
        "social_bookmark": (
            f"Title: {brand} — Solar & Electrical Panel Solutions\n"
            f"URL: https://{domain}\n"
            f"Description: Discover high-efficiency solar panels and electrical panel "
            f"products. Expert guides, product comparisons, and installation support "
            f"for residential and commercial energy projects.\n"
            f"Tags: solar-panels, electrical-panels, renewable-energy, "
            f"energy-efficiency, solar-installation"
        ),
        "press_release": (
            f"FOR IMMEDIATE RELEASE — {today}\n\n"
            f"{brand} Expands Solar Panel Solutions for Residential Customers\n\n"
            f"{brand} (https://{domain}) today announced expanded resources to help "
            f"homeowners navigate solar panel selection and installation. The company's "
            f"updated website features comprehensive guides, product comparisons, and "
            f"ROI calculators to simplify the solar buying process.\n\n"
            f"For more information, visit https://{domain}\n\n"
            f"###\nContact: info@{domain}"
        ),
        "blog_comment": (
            f"Really insightful article! One thing I'd add: the orientation and tilt "
            f"angle of panels significantly impacts output — south-facing at 30-35° is "
            f"typically optimal in the northern hemisphere. {brand} has a good "
            f"installation angle calculator at https://{domain} that accounts for "
            f"your specific latitude. Thanks for sharing this breakdown."
        ),
    }
    content = templates.get(platform_type, templates["profile_bio"])
    return f"[Ready-to-submit content for {platform_name} ({platform_type})]:\n\n{content}"


@beta_tool
def score_backlink_opportunity(
    source_url: str,
    domain_type: str,
    relevance_score: int,
    estimated_traffic: str,
    do_follow: bool,
    difficulty: str,
) -> str:
    """Score and prioritize a backlink opportunity.

    Args:
        source_url: URL of the potential linking page.
        domain_type: 'edu', 'gov', 'org', 'com', 'forum', 'directory', 'blog'.
        relevance_score: 1-10 topical relevance to solar/energy panels.
        estimated_traffic: 'high', 'medium', 'low'.
        do_follow: Whether the link would be do-follow.
        difficulty: 'easy', 'medium', 'hard'.
    """
    score = 0

    # Domain authority weight
    domain_weights = {"edu": 40, "gov": 40, "org": 25, "com": 15, "forum": 10, "directory": 10, "blog": 12}
    score += domain_weights.get(domain_type, 10)

    # Relevance
    score += relevance_score * 3

    # Traffic
    traffic_weights = {"high": 20, "medium": 10, "low": 3}
    score += traffic_weights.get(estimated_traffic, 5)

    # Do-follow bonus
    if do_follow:
        score += 15

    # Difficulty penalty
    difficulty_penalties = {"easy": 0, "medium": -5, "hard": -15}
    score += difficulty_penalties.get(difficulty, 0)

    priority = "MUST DO" if score >= 70 else "HIGH" if score >= 50 else "MEDIUM" if score >= 30 else "LOW"
    return (
        f"Opportunity Score: {score}/100 — {priority}\n"
        f"URL: {source_url}\n"
        f"Do-follow: {'Yes' if do_follow else 'No'} | "
        f"Traffic: {estimated_traffic} | Difficulty: {difficulty}\n"
        f"Relevance: {relevance_score}/10"
    )


@beta_tool
def generate_outreach_email(
    contact_name: str,
    site_name: str,
    page_topic: str,
    outreach_type: str,
    specific_value: str,
) -> str:
    """Produce a personalized outreach email for a backlink request.

    Args:
        contact_name: Name of the editor/owner (use 'there' if unknown).
        site_name: Their website or publication name.
        page_topic: Topic of their specific page relevant to your link.
        outreach_type: 'broken_link', 'guest_post', 'resource_add',
                       'unlinked_mention', 'skyscraper'.
        specific_value: What you offer: URL of content, guest post title, etc.
    """
    domain = TARGET_DOMAIN
    brand = BRAND_NAME
    subjects = {
        "broken_link": f"Broken link on your {page_topic} page",
        "guest_post": f"Guest post idea for {site_name}",
        "resource_add": f"Useful resource for your {page_topic} page",
        "unlinked_mention": f"Thanks for mentioning {brand}!",
        "skyscraper": f"Better resource for your {page_topic} readers",
    }
    bodies = {
        "broken_link": (
            f"Hi {contact_name},\n\nI was reading your page on {page_topic} at {site_name} "
            f"and noticed a broken link. I have a comprehensive, up-to-date resource on the "
            f"same topic at {specific_value} that would be a great replacement for your readers.\n\n"
            f"Would you consider swapping in the working link? Happy to reciprocate in any way.\n\n"
            f"Best,\n[Your Name]\n{brand} | https://{domain}"
        ),
        "guest_post": (
            f"Hi {contact_name},\n\nI'm a fan of {site_name}'s coverage of {page_topic}. "
            f"I write for {brand} and would love to contribute a guest post.\n\n"
            f"Proposed title: {specific_value}\n\nI can deliver 1,500–2,000 words with "
            f"original research and actionable takeaways. Would this be a good fit?\n\n"
            f"Best,\n[Your Name]\n{brand} | https://{domain}"
        ),
        "resource_add": (
            f"Hi {contact_name},\n\nYour resource page on {page_topic} is one of the best "
            f"I've found. I thought you might want to add: {specific_value}\n\nIt covers "
            f"[unique angle] and has helped thousands of readers. Let me know what you think!\n\n"
            f"Best,\n[Your Name]\n{brand} | https://{domain}"
        ),
        "unlinked_mention": (
            f"Hi {contact_name},\n\nThank you for mentioning {brand} in your article about "
            f"{page_topic} on {site_name}! We really appreciate it.\n\nWould you be open to "
            f"linking the mention directly to {specific_value}? It would help your readers "
            f"find us more easily.\n\nThanks again!\n[Your Name]\n{brand} | https://{domain}"
        ),
        "skyscraper": (
            f"Hi {contact_name},\n\nI came across your page on {page_topic} — great content. "
            f"I recently published a more comprehensive version that covers [additional angles]: "
            f"{specific_value}\n\nMight be worth linking to as an additional resource for your "
            f"readers. Happy to share data/stats from our research too.\n\n"
            f"Best,\n[Your Name]\n{brand} | https://{domain}"
        ),
    }
    subject = subjects.get(outreach_type, subjects["resource_add"])
    body = bodies.get(outreach_type, bodies["resource_add"])
    return f"Subject: {subject}\n\n{body}"


# ── Main agent runner ─────────────────────────────────────────────────────────


def run_daily_backlink_builder() -> None:
    today = datetime.date.today().isoformat()
    strategies = get_todays_strategies()

    Path(REPORTS_DIR).mkdir(exist_ok=True)

    print(f"\n{'=' * 65}")
    print(f"  Daily Backlink Builder — {TARGET_DOMAIN}")
    print(f"  Date: {today}")
    print(f"  Today's strategies: {', '.join(strategies)}")
    print(f"{'=' * 65}\n")

    log = load_log()
    log["daily_runs"].append({"date": today, "strategies": strategies})
    save_log(log)

    client = anthropic.Anthropic()

    system_prompt = f"""You are an expert off-page SEO specialist building high-quality,
relevant backlinks for {TARGET_DOMAIN} ({BRAND_NAME}) every single day.

Today's date: {today}
Niche: {NICHE}
Competitors: {', '.join(COMPETITORS)}

Your job today is to execute the following 3 strategies in sequence:
{chr(10).join(f'{i+1}. {s.replace("_", " ").title()}' for i, s in enumerate(strategies))}

For EACH strategy:
1. Use web_search to find 5+ specific, real opportunities (actual URLs, sites, forums, etc.)
2. Check get_already_done() to skip previously used sources
3. Score each opportunity with score_backlink_opportunity()
4. For the top 2-3 opportunities per strategy:
   - Generate ready-to-submit content with generate_submission_content()
   - Generate outreach emails with generate_outreach_email() where needed
   - Log everything with log_backlink()
5. Provide specific, actionable next steps for each opportunity

Strategy execution guide:
- directory_submission: Search "[niche] business directories" and "solar panels directory listing"
- forum_participation: Search site:reddit.com OR site:forum.* "[niche] recommendations"
- qa_platform: Search site:quora.com "solar panels" OR "electrical panels" questions with high traffic
- guest_post_outreach: Search "[niche] write for us" OR "[niche] guest post guidelines"
- broken_link_building: Search resource pages in niche and check for dead links
- resource_page_outreach: Search "[niche] resources" OR "best solar panel sites"
- social_bookmarking: Use platforms like Diigo, Scoop.it, Flipboard, Mix, Pocket
- competitor_backlink_gap: Search for who links to competitors but not to {TARGET_DOMAIN}
- brand_mention_conversion: Search "{BRAND_NAME}" -site:{TARGET_DOMAIN} for unlinked mentions
- niche_community_engagement: Find active LinkedIn groups, Facebook groups, Slack communities

Always be specific — use real URLs and real platform names. Never fabricate data.
End with a prioritized summary table of all opportunities found today."""

    tools = [
        log_backlink,
        get_already_done,
        generate_submission_content,
        score_backlink_opportunity,
        generate_outreach_email,
        {"type": "web_search_20260209", "name": "web_search"},
        {"type": "web_fetch_20260209", "name": "web_fetch"},
    ]

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=tools,
        system=system_prompt,
        messages=[{
            "role": "user",
            "content": (
                f"Execute today's backlink building session for {TARGET_DOMAIN}. "
                f"Today's strategies: {', '.join(strategies)}. "
                f"Find real opportunities, generate submission-ready content, "
                f"score each opportunity, log everything, and end with a clear "
                f"action plan for what to submit/send today."
            ),
        }],
    )

    report_parts = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_parts.append(block.text)

    # Save daily report
    report_path = Path(REPORTS_DIR) / f"backlinks_{today}.md"
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report — {TARGET_DOMAIN}\n")
        f.write(f"**Date:** {today}  \n")
        f.write(f"**Strategies:** {', '.join(s.replace('_', ' ').title() for s in strategies)}  \n\n")
        f.write("---\n\n")
        f.write("\n\n".join(report_parts))

    print(f"\nReport saved: {report_path}")

    # Print log summary
    log = load_log()
    print(f"\nCumulative totals:")
    print(f"  Built/submitted: {len(log['built'])}")
    print(f"  Outreach sent:   {len(log['outreach_sent'])}")
    print(f"  Opportunities:   {len(log['opportunities'])}")
    print(f"  Days run:        {len(log['daily_runs'])}")


if __name__ == "__main__":
    run_daily_backlink_builder()
