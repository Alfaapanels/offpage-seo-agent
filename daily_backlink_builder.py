"""
Daily backlink builder for alfaapanels.com
Run once per day (e.g. via cron: 0 9 * * * python /path/to/daily_backlink_builder.py)
"""

import json
import os
from datetime import date, datetime
from pathlib import Path

import anthropic
from anthropic import beta_tool

# ── Site configuration ────────────────────────────────────────────────────────

SITE_CONFIG = {
    "domain": "alfaapanels.com",
    "brand_name": "Alfa Panels",
    "niche": "panels display LED signage advertising panels",
    "competitors": [
        "novastarbmc.com",
        "colorlight.co",
        "linsn.com",
        "dbstarled.com",
    ],
    "target_pages": [
        "https://alfaapanels.com",
        "https://alfaapanels.com/products",
        "https://alfaapanels.com/about",
    ],
    "focus_keywords": [
        "LED panels",
        "display panels",
        "advertising panels",
        "LED signage",
        "video wall panels",
    ],
}

# ── Day-of-week strategy rotation ─────────────────────────────────────────────

DAILY_STRATEGY = {
    0: {  # Monday
        "name": "Directory & Citation Building",
        "task": (
            "Find 10 high-quality business directories, niche-specific directories, "
            "and citation sites where {domain} should be listed. Focus on directories "
            "related to LED technology, display manufacturing, digital signage, and B2B suppliers. "
            "Score each directory and provide submission instructions."
        ),
    },
    1: {  # Tuesday
        "name": "Resource Page Link Building",
        "task": (
            "Search for resource pages, 'best tools', 'top suppliers', and curated lists "
            "in the LED display, digital signage, and advertising technology niches that "
            "could link to {domain}. Find at least 8 promising pages and generate personalised "
            "outreach emails for the top 3."
        ),
    },
    2: {  # Wednesday
        "name": "Guest Post Prospecting",
        "task": (
            "Find 8 blogs and publications in the digital signage, LED technology, retail technology, "
            "and outdoor advertising niches that accept guest posts. Evaluate each for domain authority "
            "signals and audience fit. Generate a guest post pitch email for the top 2 prospects, "
            "suggesting a specific article topic relevant to {domain}'s expertise."
        ),
    },
    3: {  # Thursday
        "name": "Broken Link Building",
        "task": (
            "Search for broken or outdated resource pages in the LED panel, display screen, "
            "and digital signage space. Look for pages that link to dead competitor sites or "
            "obsolete product pages. Identify at least 5 broken-link opportunities and generate "
            "replacement outreach emails referencing specific {domain} content."
        ),
    },
    4: {  # Friday
        "name": "Competitor Backlink Gap Analysis",
        "task": (
            "Analyse the backlink profiles of {competitors} by searching for pages that mention "
            "or link to them. Identify websites, blogs, and directories that link to competitors "
            "but not to {domain}. Rank the top 5 gap opportunities by potential value and suggest "
            "an angle for earning each link."
        ),
    },
    5: {  # Saturday
        "name": "Forum & Community Participation",
        "task": (
            "Find active forums, Reddit communities, LinkedIn groups, Quora spaces, and niche "
            "communities discussing LED panels, digital signage, advertising displays, and related topics. "
            "Identify 6 threads or questions where a genuine, helpful response mentioning {domain} "
            "would be appropriate. Draft example responses."
        ),
    },
    6: {  # Sunday
        "name": "Brand Mention & Unlinked Citation Outreach",
        "task": (
            "Search the web for unlinked brand mentions of '{brand_name}' and '{domain}'. "
            "Find at least 5 pages that mention the brand without a hyperlink. "
            "Also search for reviews, press mentions, and social media posts. "
            "Generate polite link-request emails for each unlinked mention found."
        ),
    },
}

# ── State tracker ─────────────────────────────────────────────────────────────

STATE_FILE = Path("backlink_state.json")


def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"pursued_urls": [], "daily_runs": [], "total_opportunities": 0}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def record_run(state: dict, strategy_name: str, report_file: str, opportunities: int) -> None:
    state["daily_runs"].append(
        {
            "date": str(date.today()),
            "strategy": strategy_name,
            "report": report_file,
            "opportunities_found": opportunities,
        }
    )
    state["total_opportunities"] += opportunities
    save_state(state)


# ── Tools ─────────────────────────────────────────────────────────────────────

@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to a URL.

    Args:
        url: Your target URL.
        backlink_url: The URL linking to you.
        anchor_text: The anchor text used in the link.
    """
    quality_signals = []
    generic = ["click here", "website", "here", "link", "read more"]
    if anchor_text.lower() in generic:
        quality_signals.append("Warning: Generic anchor text - low value")
    else:
        quality_signals.append(f"Good: Descriptive anchor: '{anchor_text}'")
    toxic_signals = ["spam", "casino", "viagra", "porn", "adult"]
    if any(t in backlink_url.lower() for t in toxic_signals):
        quality_signals.append("TOXIC link - disavow recommended")
    else:
        quality_signals.append("Domain appears clean")
    authority_bonus = ""
    for tld in [".edu", ".gov", ".org"]:
        if tld in backlink_url:
            authority_bonus = f" | HIGH AUTHORITY TLD ({tld})"
            break
    return "\n".join(quality_signals) + authority_bonus


@beta_tool
def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    """Categorize a brand mention as linked/unlinked and detect sentiment.

    Args:
        mention_text: The text containing the brand mention.
        brand_name: Your brand or website name.
    """
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive = ["great", "best", "excellent", "recommend", "love", "amazing", "quality", "reliable"]
    negative = ["bad", "worst", "avoid", "scam", "terrible", "poor", "cheap", "broken"]
    pos = sum(1 for w in positive if w in mention_text.lower())
    neg = sum(1 for w in negative if w in mention_text.lower())
    sentiment = "Positive" if pos > neg else ("Negative" if neg > pos else "Neutral")
    mention_type = "Linked mention" if has_link else "Unlinked mention (link building opportunity!)"
    action = "Monitor & engage" if has_link else "Reach out to add your link"
    return (
        f"Brand: {brand_name}\nType: {mention_type}\nSentiment: {sentiment}\nAction: {action}"
    )


@beta_tool
def score_link_prospect(
    page_url: str, page_title: str, page_content_snippet: str, your_niche: str
) -> str:
    """Score a potential link-building prospect out of 100.

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
    high_value = ["resource", "guide", "tools", "blog", "list", "best", "top", "review", "supplier"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value):
        score += 30
        reasons.append("Resource/guide/list page - high link value (+30)")
    for tld in [".edu", ".gov", ".org"]:
        if tld in page_url:
            score += 30
            reasons.append(f"High-authority domain {tld} (+30)")
            break
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH PRIORITY" if score >= 70 else ("MEDIUM" if score >= 40 else "LOW")
    return f"Score: {score}/100 [{priority}]\nURL: {page_url}\n" + "\n".join(reasons)


@beta_tool
def generate_outreach_template(
    prospect_name: str,
    prospect_site: str,
    their_page_topic: str,
    your_site: str,
    your_content_url: str,
    link_type: str,
) -> str:
    """Generate a personalised outreach email for link building.

    Args:
        prospect_name: Name of the website owner/editor.
        prospect_site: Their website name.
        their_page_topic: Topic of the page where you want a link.
        your_site: Your website name.
        your_content_url: URL of your content to be linked.
        link_type: One of 'guest_post', 'broken_link', 'resource', 'mention', 'directory'.
    """
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I was reading your excellent article on {their_page_topic} at {prospect_site} "
            f"and noticed one of the links appears to be broken.\n\n"
            f"I've created a comprehensive resource at {your_content_url} from {your_site} "
            f"that covers the same topic and would serve as a great replacement.\n\n"
            f"Would you be open to updating that link?\n\nBest,\n[Your Name] – {your_site}"
        ),
        "guest_post": (
            f"Subject: Guest Post Pitch for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I really enjoy your content about {their_page_topic} on {prospect_site}. "
            f"I write for {your_site} and think your audience would benefit from a deep-dive on "
            f"[specific angle related to {their_page_topic}].\n\n"
            f"I'd love to contribute a guest post. Happy to share a full outline first.\n\n"
            f"Interested?\n\nBest,\n[Your Name] – {your_site}"
        ),
        "resource": (
            f"Subject: Addition suggestion for your {their_page_topic} resource page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is one of the best I've seen! "
            f"I noticed you haven't included {your_site} yet – we've published {your_content_url} "
            f"which has helped thousands of professionals in this space.\n\n"
            f"Would you consider adding it to your list?\n\nThanks,\n[Your Name] – {your_site}"
        ),
        "mention": (
            f"Subject: You mentioned {your_site} – thank you!\n\n"
            f"Hi {prospect_name},\n\n"
            f"I just came across your article on {their_page_topic} at {prospect_site} "
            f"and was thrilled to see {your_site} mentioned – thank you!\n\n"
            f"I was wondering if you'd be open to turning that mention into a hyperlink "
            f"pointing to {your_content_url}? It would make it easy for your readers to find us.\n\n"
            f"Happy to return the favour!\n\nBest,\n[Your Name] – {your_site}"
        ),
        "directory": (
            f"Subject: Listing submission for {your_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I'd like to submit {your_site} for inclusion in your {their_page_topic} directory.\n\n"
            f"We are a leading supplier of LED display panels and advertising solutions. "
            f"Our listing page: {your_content_url}\n\n"
            f"Please let me know if you need any additional information.\n\n"
            f"Best,\n[Your Name] – {your_site}"
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
        f"LINK GAP OPPORTUNITY\n"
        f"Competitor: {competitor_domain}\n"
        f"Your site: {your_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Action plan:\n"
        f"1. Identify the specific content on {competitor_domain} that earned this link\n"
        f"2. Create a better or more up-to-date version of that content for {your_domain}\n"
        f"3. Reach out to the linking page owner with your improved resource\n"
        f"4. Highlight what makes {your_domain}'s version superior"
    )


@beta_tool
def log_backlink_opportunity(url: str, opportunity_type: str, priority: str, notes: str) -> str:
    """Log a discovered backlink opportunity to the state file.

    Args:
        url: The opportunity URL.
        opportunity_type: Type such as 'directory', 'guest_post', 'resource', 'broken_link', 'mention'.
        priority: 'high', 'medium', or 'low'.
        notes: Brief notes about the opportunity.
    """
    state = load_state()
    if url not in state["pursued_urls"]:
        state.setdefault("opportunities", []).append(
            {
                "url": url,
                "type": opportunity_type,
                "priority": priority,
                "notes": notes,
                "discovered": str(date.today()),
                "status": "pending",
            }
        )
        state["total_opportunities"] += 1
        save_state(state)
        return f"Logged: [{priority.upper()}] {opportunity_type} – {url}"
    return f"Already tracked: {url}"


# ── Daily runner ──────────────────────────────────────────────────────────────

def run_daily_backlink_campaign() -> None:
    client = anthropic.Anthropic()
    state = load_state()
    today = date.today()
    weekday = today.weekday()  # 0=Monday … 6=Sunday
    strategy = DAILY_STRATEGY[weekday]
    cfg = SITE_CONFIG

    already_run_today = any(r["date"] == str(today) for r in state.get("daily_runs", []))
    if already_run_today:
        print(f"[{today}] Already ran today – skipping.")
        return

    task_prompt = strategy["task"].format(
        domain=cfg["domain"],
        brand_name=cfg["brand_name"],
        competitors=", ".join(cfg["competitors"]),
    )

    pursued_preview = state["pursued_urls"][-20:] if state["pursued_urls"] else []

    system_prompt = f"""You are an expert off-page SEO strategist working exclusively for {cfg['domain']}.

Site details:
- Domain: {cfg['domain']}
- Brand: {cfg['brand_name']}
- Niche: {cfg['niche']}
- Focus keywords: {', '.join(cfg['focus_keywords'])}
- Competitors: {', '.join(cfg['competitors'])}

Today's date: {today} (Day {weekday + 1}/7)
Today's strategy: {strategy['name']}

Already pursued (avoid repeating these):
{json.dumps(pursued_preview, indent=2) if pursued_preview else 'None yet'}

IMPORTANT RULES:
1. Use web_search and web_fetch tools to discover REAL, currently active opportunities.
2. Use score_link_prospect to evaluate every prospect before including it.
3. Use generate_outreach_template to create ready-to-send emails for top prospects.
4. Use log_backlink_opportunity to record every actionable find.
5. Prioritise relevance: only recommend sites in the LED/display/signage/advertising/B2B tech space.
6. End with a concise summary table: URL | Type | Priority | Next Action."""

    print(f"\n{'='*65}")
    print(f"  Daily Backlink Builder – {cfg['domain']}")
    print(f"  Date: {today}  |  Strategy: {strategy['name']}")
    print(f"{'='*65}\n")

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        system=system_prompt,
        tools=[
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            log_backlink_opportunity,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{"role": "user", "content": task_prompt}],
        betas=["web-search-2025-03-05"],
    )

    report_parts = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_parts.append(block.text)

    # Save dated report
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    report_file = str(reports_dir / f"{today}_{strategy['name'].lower().replace(' ', '_')}.md")
    with open(report_file, "w") as f:
        f.write(f"# Backlink Report: {cfg['domain']}\n")
        f.write(f"**Date:** {today}  |  **Strategy:** {strategy['name']}\n\n")
        f.write("\n\n".join(report_parts))

    # Reload state to count today's newly logged opportunities
    fresh_state = load_state()
    new_today = sum(
        1
        for opp in fresh_state.get("opportunities", [])
        if opp.get("discovered") == str(today)
    )
    record_run(fresh_state, strategy["name"], report_file, new_today)

    print(f"\nReport saved → {report_file}")
    print(f"New opportunities logged today: {new_today}")
    print(f"Total opportunities in pipeline: {fresh_state['total_opportunities']}")


if __name__ == "__main__":
    run_daily_backlink_campaign()
