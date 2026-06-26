"""
Off-Page SEO utilities for alfaapanels.com.

These helper functions are used by the Claude Code SEO agent when it runs daily.
The agent (Claude Code) orchestrates web research directly; these are analysis helpers.
"""

from datetime import date
import os
import subprocess
import sys

DOMAIN = "alfaapanels.com"
BRAND = "Alfaa Panels"
NICHE = "insulated sandwich panels PUF PIR EPS rockwool cold room clean room manufacturer India"
COMPETITORS = ["epack.in", "isothermpufpanel.com", "industrialfoams.com"]


def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to a URL."""
    quality_signals = []
    exact_match_keywords = ["click here", "website", "here", "link"]
    if anchor_text.lower() in exact_match_keywords:
        quality_signals.append("Warning: Generic anchor text - low value")
    else:
        quality_signals.append(f"Good: Descriptive anchor: '{anchor_text}'")
    if any(word in backlink_url.lower() for word in ["spam", "casino", "viagra"]):
        quality_signals.append("TOXIC link - disavow recommended")
    else:
        quality_signals.append("Domain appears clean")
    return "\n".join(quality_signals)


def categorize_brand_mention(mention_text: str, brand_name: str = BRAND) -> str:
    """Categorize a brand mention as linked/unlinked and sentiment."""
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing", "quality", "reliable", "trusted"]
    negative_words = ["bad", "worst", "avoid", "scam", "terrible", "poor", "delayed", "fake"]
    pos_score = sum(1 for w in positive_words if w in mention_text.lower())
    neg_score = sum(1 for w in negative_words if w in mention_text.lower())
    if pos_score > neg_score:
        sentiment = "Positive"
    elif neg_score > pos_score:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    mention_type = "Linked mention" if has_link else "Unlinked mention (link building opportunity!)"
    return (
        f"Brand: {brand_name}\n"
        f"Type: {mention_type}\n"
        f"Sentiment: {sentiment}\n"
        f"Action: {'Monitor' if has_link else 'Reach out to add your link'}"
    )


def score_link_prospect(page_url: str, page_title: str, page_content_snippet: str, niche: str = NICHE) -> str:
    """Score a potential link building prospect (0-100)."""
    score = 0
    reasons = []
    niche_words = niche.lower().split()
    content_lower = (page_title + " " + page_content_snippet).lower()
    relevance = sum(1 for word in niche_words if word in content_lower)
    if relevance >= 3:
        score += 40
        reasons.append("High niche relevance (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "directory", "supplier", "manufacturer"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/directory page (+30)")
    authority_signals = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority_signals):
        score += 30
        reasons.append("High authority domain (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH PRIORITY" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Score: {score}/100 - {priority}\nURL: {page_url}\n" + "\n".join(f"  - {r}" for r in reasons)


def generate_outreach_template(
    prospect_name: str,
    prospect_site: str,
    their_page_topic: str,
    your_content_url: str,
    link_type: str,
) -> str:
    """Generate a personalized outreach email for link building."""
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I came across your {their_page_topic} page on {prospect_site} and noticed a broken link.\n\n"
            f"We have a resource at {your_content_url} from Alfaa Panels — India's leading sandwich panel "
            f"manufacturer — that would be a perfect replacement.\n\n"
            f"Would you consider updating the link?\n\nBest regards,\nAlfaa Panels | info@alfaapanels.com"
        ),
        "guest_post": (
            f"Subject: Guest Post Contribution for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I've been following {prospect_site} and really enjoy your content on {their_page_topic}.\n\n"
            f"I represent Alfaa Panels (alfaapanels.com), a leading sandwich panel manufacturer in India. "
            f"We'd love to contribute a guest article on topics like insulated panel selection, cold room "
            f"construction, or energy-efficient building — highly relevant to your audience.\n\n"
            f"Would you be open to a collaboration?\n\nBest regards,\nAlfaa Panels | info@alfaapanels.com"
        ),
        "resource": (
            f"Subject: Useful resource for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is excellent! I'd like to suggest a resource "
            f"from Alfaa Panels: {your_content_url}\n\n"
            f"We manufacture PUF, PIR, EPS, rockwool, cold room, and clean room sandwich panels across India "
            f"— this resource might add real value for your readers.\n\n"
            f"Would you take a look?\n\nBest regards,\nAlfaa Panels | info@alfaapanels.com"
        ),
        "mention": (
            f"Subject: You mentioned Alfaa Panels — thank you!\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning Alfaa Panels in your article about {their_page_topic} on {prospect_site}!\n\n"
            f"Would you be open to adding a direct link to {your_content_url}? It would help your readers "
            f"find the product details easily.\n\nThanks,\nAlfaa Panels | info@alfaapanels.com"
        ),
    }
    return templates.get(link_type, templates["resource"])


def save_report(content: str, today: str = None) -> str:
    """Save report to dated file in reports/ directory."""
    today = today or date.today().isoformat()
    os.makedirs("reports", exist_ok=True)
    filename = f"reports/seo_report_{today}.md"
    with open(filename, "w") as f:
        f.write(f"# Off-Page SEO Report: {DOMAIN}\n")
        f.write(f"**Date:** {today}\n\n")
        f.write(content)
    return filename


def git_commit_and_push(report_filename: str, today: str = None) -> bool:
    """Commit and push the report to the repo."""
    today = today or date.today().isoformat()
    branch = "claude/friendly-euler-qnvo9e"
    cmds = [
        ["git", "add", report_filename],
        ["git", "commit", "-m", f"feat: daily SEO backlink report {today}"],
        ["git", "push", "-u", "origin", branch],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        if result.returncode != 0 and "nothing to commit" not in result.stderr:
            print(f"Git warning: {result.stderr.strip()}", file=sys.stderr)
            return False
    return True


if __name__ == "__main__":
    # Quick self-test of the utility functions
    print(score_link_prospect(
        "https://indiamart.com/companydir/puf-panel-manufacturers.html",
        "Top PUF Panel Manufacturers in India - IndiaMART Directory",
        "Find verified PUF panel, sandwich panel, cold room panel manufacturers",
    ))
    print()
    print(generate_outreach_template(
        prospect_name="Editor",
        prospect_site="constructionworld.in",
        their_page_topic="building insulation materials",
        your_content_url="https://alfaapanels.com/product/puf-wall-panel/",
        link_type="resource",
    ))
