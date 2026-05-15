import anthropic
from anthropic import beta_tool
import json
import os
from collections import Counter
from datetime import date

client = anthropic.Anthropic()

# ── Site configuration ──────────────────────────────────────────────────────
DOMAIN = "alfaapanels.com"
BRAND = "Alfa Panels"
NICHE = "solar panels electrical panels building panels manufacturing supplier"
COMPETITORS = ["paneltech.com", "alphasolar.net", "buildingpanelspro.com"]
BACKLINKS_LOG = "built_backlinks.json"


# ── Backlink log helpers ────────────────────────────────────────────────────

def _load_log() -> dict:
    if os.path.exists(BACKLINKS_LOG):
        with open(BACKLINKS_LOG) as f:
            return json.load(f)
    return {}


def _save_log(log: dict) -> None:
    with open(BACKLINKS_LOG, "w") as f:
        json.dump(log, f, indent=2)


# ── Tools ───────────────────────────────────────────────────────────────────

@beta_tool
def track_built_backlink(
    backlink_url: str,
    backlink_type: str,
    anchor_text: str,
    status: str = "found",
) -> str:
    """Record a backlink opportunity to avoid duplicates in future runs.

    Args:
        backlink_url: The URL where the backlink was or will be placed.
        backlink_type: Type: 'directory', 'guest_post', 'forum', 'social', 'resource', 'mention_conversion', 'broken_link'.
        anchor_text: The anchor text used or planned.
        status: Status: 'found', 'submitted', 'live', 'pending_review'.
    """
    log = _load_log()
    if backlink_url in log:
        entry = log[backlink_url]
        return (
            f"ALREADY TRACKED: {backlink_url}\n"
            f"First recorded: {entry['date']} | Type: {entry['type']} | Status: {entry['status']}"
        )
    log[backlink_url] = {
        "date": date.today().isoformat(),
        "type": backlink_type,
        "anchor": anchor_text,
        "status": status,
    }
    _save_log(log)
    return (
        f"TRACKED: New {backlink_type} opportunity\n"
        f"URL: {backlink_url}\nAnchor: '{anchor_text}' | Status: {status}"
    )


@beta_tool
def get_backlink_stats(placeholder: str = "") -> str:
    """Get a summary of all backlink opportunities tracked so far for alfaapanels.com.

    Args:
        placeholder: Not used — pass an empty string.
    """
    log = _load_log()
    if not log:
        return "No backlinks tracked yet — this is the first run!"
    types = Counter(v["type"] for v in log.values())
    statuses = Counter(v["status"] for v in log.values())
    recent = sorted(log.items(), key=lambda x: x[1]["date"], reverse=True)[:5]
    lines = [
        f"Total opportunities tracked: {len(log)}",
        f"By type: {dict(types)}",
        f"By status: {dict(statuses)}",
        "5 most recent entries:",
    ]
    for url, data in recent:
        lines.append(f"  [{data['date']}] {data['type']:18s} {data['status']:16s} {url}")
    return "\n".join(lines)


@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to a URL.

    Args:
        url: Your target URL.
        backlink_url: The URL that would link to you.
        anchor_text: The anchor text used in the link.
    """
    signals = []
    generic = ["click here", "website", "here", "link", "read more"]
    if anchor_text.lower() in generic:
        signals.append("Warning: Generic anchor text — low value")
    else:
        signals.append(f"Good: Descriptive anchor '{anchor_text}'")
    toxic = ["spam", "casino", "viagra", "adult", "porn"]
    if any(w in backlink_url.lower() for w in toxic):
        signals.append("TOXIC domain — skip")
    else:
        signals.append("Domain appears clean")
    if any(s in backlink_url for s in [".edu", ".gov", ".org"]):
        signals.append("High-authority domain — HIGH PRIORITY")
    return "\n".join(signals)


@beta_tool
def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    """Categorise a brand mention as linked/unlinked and by sentiment.

    Args:
        mention_text: The text containing the brand mention.
        brand_name: Your brand or website name.
    """
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    pos = ["great", "best", "excellent", "recommend", "quality", "reliable", "trusted"]
    neg = ["bad", "worst", "avoid", "scam", "terrible", "poor", "cheap"]
    pos_score = sum(1 for w in pos if w in mention_text.lower())
    neg_score = sum(1 for w in neg if w in mention_text.lower())
    sentiment = "Positive" if pos_score > neg_score else "Negative" if neg_score > pos_score else "Neutral"
    mention_type = "Linked mention" if has_link else "Unlinked mention (backlink opportunity!)"
    action = "Monitor" if has_link else "Reach out to convert this into a backlink"
    return f"Brand: {brand_name}\nType: {mention_type}\nSentiment: {sentiment}\nAction: {action}"


@beta_tool
def score_link_prospect(
    page_url: str, page_title: str, page_content_snippet: str, your_niche: str
) -> str:
    """Score a potential link-building prospect out of 100.

    Args:
        page_url: URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: Short snippet of the page content.
        your_niche: Your website niche/topic keywords.
    """
    score = 0
    reasons = []
    niche_words = your_niche.lower().split()
    content_lower = (page_title + " " + page_content_snippet).lower()
    relevance = sum(1 for w in niche_words if w in content_lower)
    if relevance >= 3:
        score += 40
        reasons.append("High niche relevance (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate niche relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    high_value = ["resource", "guide", "tools", "blog", "list", "best", "directory", "supplier"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value):
        score += 30
        reasons.append("Resource/directory page (+30)")
    if any(s in page_url for s in [".edu", ".gov", ".org"]):
        score += 30
        reasons.append("High-authority domain (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH PRIORITY" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Score: {score}/100 — {priority}\nURL: {page_url}\n" + "\n".join(reasons)


@beta_tool
def generate_outreach_template(
    prospect_name: str,
    prospect_site: str,
    their_page_topic: str,
    your_content_url: str,
    link_type: str,
) -> str:
    """Generate a personalised outreach email for link building.

    Args:
        prospect_name: Name of the website owner/editor (use 'Team' if unknown).
        prospect_site: Their website name.
        their_page_topic: Topic of the page where you want a link.
        your_content_url: URL of your content to be linked.
        link_type: Type: 'guest_post', 'broken_link', 'resource', 'mention', 'directory'.
    """
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I came across a broken link on your {their_page_topic} page on {prospect_site}.\n\n"
            f"We have a comprehensive resource at {your_content_url} that would be a great "
            f"replacement for your readers.\n\n"
            f"Would you consider updating the link?\n\nBest regards,\n[Your Name] | Alfa Panels\nalfaapanels.com"
        ),
        "guest_post": (
            f"Subject: Guest Post Idea for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I've been enjoying your content on {prospect_site}, especially around {their_page_topic}.\n\n"
            f"I'm from Alfa Panels (alfaapanels.com) and would love to contribute a guest post "
            f"with actionable insights on panels solutions for your audience.\n\n"
            f"Would you be open to a collaboration?\n\nBest regards,\n[Your Name] | Alfa Panels"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is excellent! I believe our guide at "
            f"{your_content_url} would be a valuable addition for your readers.\n\n"
            f"Would you consider including it?\n\nBest regards,\n[Your Name] | Alfa Panels\nalfaapanels.com"
        ),
        "mention": (
            f"Subject: Thank you for mentioning Alfa Panels!\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning Alfa Panels in your article about {their_page_topic} on {prospect_site}!\n\n"
            f"Would you be open to linking directly to {your_content_url} so your readers can "
            f"find us easily?\n\nThanks,\n[Your Name] | Alfa Panels\nalfaapanels.com"
        ),
        "directory": (
            f"Subject: Listing submission — Alfa Panels\n\n"
            f"Hi {prospect_name},\n\n"
            f"I'd like to submit Alfa Panels to {prospect_site} under the {their_page_topic} category.\n\n"
            f"Site: alfaapanels.com\n"
            f"Business Name: Alfa Panels\n"
            f"Description: Premium panels solutions for solar, electrical, and building applications. "
            f"Quality products, competitive pricing, and expert support.\n"
            f"Category: {their_page_topic}\n\n"
            f"Thank you!\n[Your Name] | Alfa Panels"
        ),
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def identify_link_gap_opportunity(
    competitor_domain: str, linking_page_topic: str
) -> str:
    """Identify a competitor backlink as a gap opportunity for alfaapanels.com.

    Args:
        competitor_domain: Competitor's domain.
        linking_page_topic: Topic of the page linking to the competitor.
    """
    return (
        f"LINK GAP OPPORTUNITY\n"
        f"Competitor: {competitor_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Actions:\n"
        f"1. Find the specific content that earned {competitor_domain} this link\n"
        f"2. Create a better / more comprehensive resource on '{linking_page_topic}' for {DOMAIN}\n"
        f"3. Reach out to the linking page with your superior content as a replacement or addition"
    )


# ── Main agent ──────────────────────────────────────────────────────────────

def run_offpage_seo_agent(
    your_domain: str = DOMAIN,
    brand_name: str = BRAND,
    niche: str = NICHE,
    competitors: list = None,
) -> None:
    if competitors is None:
        competitors = COMPETITORS
    today = date.today().isoformat()
    print(f"\n{'='*60}")
    print(f"Daily Backlink Builder | {today}")
    print(f"Target: {your_domain}")
    print("=" * 60)

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-7",
        max_tokens=16000,
        tools=[
            track_built_backlink,
            get_backlink_stats,
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO specialist building backlinks daily for {your_domain}.
Today: {today} | Brand: {brand_name} | Niche: {niche}
Competitors: {', '.join(competitors)}

Work through every task below using tools at each step. Be thorough — the goal is to find
and track real, relevant backlink opportunities that will improve {your_domain}'s authority.

TASK 1 — Progress Check
Call get_backlink_stats("") to review what has already been tracked. Note gaps in coverage.

TASK 2 — Directory Submissions
Search: "{niche} business directory free submit" and "{niche} supplier directory listing"
For each directory found: score it with score_link_prospect. If score ≥ 40, call
track_built_backlink (type='directory') and generate_outreach_template (type='directory').
Target: find and track at least 5 relevant directories.

TASK 3 — Brand Mention Audit
Search: '"{brand_name}"' -site:{your_domain}
For each unlinked mention: call categorize_brand_mention, then fetch the page with
web_fetch to confirm it's real, then generate_outreach_template (type='mention') and
track_built_backlink (type='mention_conversion').

TASK 4 — Competitor Backlink Gaps
For each competitor [{', '.join(competitors)}]:
  Search: "{competitor} panels supplier review site" and "alfaapanels competitor"
  For 2-3 linking pages: call identify_link_gap_opportunity, score with score_link_prospect,
  and track top opportunities (type='resource').

TASK 5 — Guest Post & Resource Pages
Search: "{niche} write for us" and "{niche} contribute guest post" and
        "{niche} resources page add link"
Score each with score_link_prospect. For prospects scoring ≥ 50: generate_outreach_template
(type='guest_post' or 'resource') and track them.

TASK 6 — Forum & Community Presence
Search: "{niche} forum community reddit linkedin group"
Find 3-5 relevant communities. Track them (type='forum') for future participation.

TASK 7 — Broken Link Opportunities
Search: "{niche} broken link checker" and "{niche} useful resources 404"
If you find broken link pages in the niche, score them and generate broken_link outreach.

TASK 8 — Daily Summary Report
List ALL new opportunities found today (minimum 10). For each include:
  • URL
  • Type (directory / guest_post / resource / mention / forum)
  • Score
  • Recommended action
  • Outreach template (if generated)

Finish with a prioritised TOP 5 actions to take today, ranked by expected SEO impact.""",
        }],
    )

    full_report: list[str] = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    report_path = f"backlink_report_{your_domain.replace('.', '_')}_{today}.md"
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report: {your_domain}\n**Date:** {today}\n\n")
        f.write("\n\n".join(full_report))
    print(f"\nReport saved: {report_path}")


if __name__ == "__main__":
    run_offpage_seo_agent()
