#!/usr/bin/env python3
"""
Daily Backlink Builder for alfaapanels.com
Rotates through 7 link-building strategies, one per day of the week.
Tracks every discovered opportunity and generates ready-to-send outreach.
"""

import json
import datetime
from pathlib import Path

import anthropic
from anthropic import beta_tool

# ── Site configuration ────────────────────────────────────────────────────────

SITE = {
    "domain": "alfaapanels.com",
    "brand": "Alfa Panels",
    "niche": "aluminum composite panels facade cladding building materials ACP ACM",
    "industry": "construction architecture building materials",
    "competitors": [
        "alucobond.com",
        "reynobond.com",
        "alpolic.com",
        "alucoworld.com",
    ],
    "target_keywords": [
        "aluminum composite panels",
        "ACP panels",
        "ACM panels",
        "aluminium cladding",
        "facade cladding panels",
        "building facade materials",
        "composite cladding",
        "exterior wall panels",
    ],
    "pages": {
        "home": "https://alfaapanels.com",
        "products": "https://alfaapanels.com/products",
        "about": "https://alfaapanels.com/about",
        "contact": "https://alfaapanels.com/contact",
    },
}

STATE_FILE = Path("backlink_state.json")
REPORTS_DIR = Path("reports")

# Day-of-week strategy rotation
STRATEGY_BY_DAY = {
    0: "brand_mentions",     # Monday
    1: "competitor_gaps",    # Tuesday
    2: "resource_pages",     # Wednesday
    3: "guest_posts",        # Thursday
    4: "broken_links",       # Friday
    5: "directories",        # Saturday
    6: "forums_qa",          # Sunday
}

STRATEGY_TASKS = {
    "brand_mentions": f"""
TODAY'S FOCUS: Brand Mention Conversion

Search for "{SITE['brand']}" and "alfaapanels.com" mentions that exist online without a link back to the site.

1. Search: "{SITE['brand']}" -site:alfaapanels.com
2. Search: "alfaapanels" -site:alfaapanels.com
3. Search: "alfa panels" building materials -site:alfaapanels.com
4. For every unlinked mention found: use track_opportunity() and generate_outreach_email(link_type="mention")
5. Prioritise positive mentions on high-traffic sites first
""",

    "competitor_gaps": f"""
TODAY'S FOCUS: Competitor Backlink Gap Analysis

Find sites linking to our competitors but NOT to alfaapanels.com — these are warm prospects because the page is already proven to link to ACP panel suppliers.

Competitors: {', '.join(SITE['competitors'])}

1. Search: link building sources for each competitor (e.g. "alucobond.com" site listings, mentions)
2. Search: pages that reference or recommend alucobond OR reynobond OR alpolic
3. For each opportunity: use identify_link_gap() then score_link_prospect()
4. Generate outreach for the top 5 gaps using generate_outreach_email(link_type="resource")
""",

    "resource_pages": f"""
TODAY'S FOCUS: Resource Page Link Building

Find resource, link list, and tools pages in construction / architecture niches that could list alfaapanels.com.

1. Search: "aluminum composite panels" "resources" OR "useful links" OR "recommended"
2. Search: architects resources building materials links site:.org OR site:.edu
3. Search: construction materials directory list site
4. Search: ACP panels guide resources
5. Score each page with score_link_prospect()
6. Generate resource outreach emails for the top 5 scoring pages
""",

    "guest_posts": f"""
TODAY'S FOCUS: Guest Post Opportunities

Find blogs, trade publications, and industry sites that accept guest contributions and cover architecture, construction, or building materials.

1. Search: "write for us" (architecture OR construction OR "building materials")
2. Search: "guest post" (aluminum panels OR facade cladding OR ACP)
3. Search: "submit an article" architect contractor builder blog
4. Search: trade publication construction materials contributor guidelines
5. Score prospects with score_link_prospect()
6. Generate a compelling guest post pitch email for each top prospect using generate_outreach_email(link_type="guest_post")
""",

    "broken_links": f"""
TODAY'S FOCUS: Broken Link Building

Find pages in relevant niches that contain dead or broken links alfaapanels.com content could replace.

1. Search: "aluminum composite panels" resources site:.org OR site:.edu OR site:.gov
2. Fetch several promising resource pages and look for signs of outdated content or dead external links
3. Search: ACP panels guide resources outdated
4. Search: aluminium cladding broken link resource page
5. For each broken-link opportunity: identify which alfaapanels.com page is the best replacement
6. Generate broken link outreach using generate_outreach_email(link_type="broken_link")
""",

    "directories": f"""
TODAY'S FOCUS: Directory & Citation Building

Find relevant business, industry, and niche directories where alfaapanels.com should be listed.

1. Search: aluminum composite panel manufacturer directory listing submit
2. Search: building materials supplier directory free submission
3. Search: construction company directory add listing
4. Search: architecture products directory submission
5. Search: B2B building materials marketplace listing
6. For each directory found: note the submission URL, requirements, whether it's free/paid
7. Track each with track_opportunity(opportunity_type="directory")
8. Prioritise free, dofollow, niche-relevant directories first
""",

    "forums_qa": f"""
TODAY'S FOCUS: Forum & Q&A Participation

Find active threads and unanswered questions where alfaapanels.com's expertise genuinely adds value.

1. Search: site:reddit.com "aluminum composite panels" OR "ACP panels" questions 2024 OR 2025
2. Search: site:quora.com "aluminium cladding" OR "facade panels" unanswered
3. Search: construction forum "aluminum panels" OR "ACP" questions recommendations
4. Search: architect forum "building materials" panel recommendations
5. Search: Houzz OR ArchDaily forum aluminum cladding discussion
6. For each thread: note the URL, question, best alfaapanels.com resource to reference
7. Track with track_opportunity(opportunity_type="forum")
8. Draft a helpful, expert answer for the top 5 questions (include how alfaapanels.com can help without being spammy)
""",
}


# ── Persistence ───────────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"opportunities": [], "runs": [], "links_built": []}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)


# ── Tools ─────────────────────────────────────────────────────────────────────

@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate the SEO quality of a backlink pointing to our site.

    Args:
        url: The target URL on alfaapanels.com being linked to.
        backlink_url: The URL of the page that contains the link.
        anchor_text: The anchor text used in the link.
    """
    signals = []
    generic = {"click here", "here", "website", "link", "read more", "visit"}
    if anchor_text.lower().strip() in generic:
        signals.append(f"Weak anchor '{anchor_text}' — low SEO value")
    else:
        signals.append(f"Descriptive anchor '{anchor_text}' — good SEO value")

    toxic = ["spam", "casino", "gambling", "viagra", "porn", "adult", "payday"]
    if any(t in backlink_url.lower() for t in toxic):
        signals.append("TOXIC domain — recommend disavow")
    else:
        signals.append("Domain appears clean")

    if any(tld in backlink_url for tld in [".edu", ".gov"]):
        signals.append("Authority TLD (.edu/.gov) — very high link value")
    elif ".org" in backlink_url:
        signals.append("Non-profit TLD (.org) — elevated link value")

    return "\n".join(signals)


@beta_tool
def score_link_prospect(
    page_url: str,
    page_title: str,
    page_content_snippet: str,
    your_niche: str,
) -> str:
    """Score a link-building prospect from 0 to 100.

    Args:
        page_url: Full URL of the prospect page.
        page_title: Page title tag text.
        page_content_snippet: Short excerpt of the page body.
        your_niche: Niche descriptor (e.g. "aluminum composite panels cladding").
    """
    score = 0
    reasons = []

    niche_words = your_niche.lower().split()
    body = (page_title + " " + page_content_snippet).lower()
    hits = sum(1 for w in niche_words if w in body)
    if hits >= 3:
        score += 40
        reasons.append("High niche relevance (+40)")
    elif hits >= 1:
        score += 20
        reasons.append("Moderate niche relevance (+20)")
    else:
        reasons.append("Low relevance (+0)")

    resource_signals = ["resource", "guide", "directory", "tools", "list", "top", "best", "links"]
    if any(s in page_url.lower() or s in page_title.lower() for s in resource_signals):
        score += 30
        reasons.append("Resource/directory page — high link opportunity (+30)")

    if any(tld in page_url for tld in [".edu", ".gov"]):
        score += 30
        reasons.append("Authority TLD (+30)")
    elif ".org" in page_url:
        score += 20
        reasons.append("Non-profit domain (+20)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")

    priority = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return (
        f"Score: {score}/100  Priority: {priority}\n"
        f"URL: {page_url}\n"
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
    """Generate a personalised outreach email for a link-building prospect.

    Args:
        prospect_name: First name or job title of the contact (e.g. "Sarah" or "Editor").
        prospect_site: Name of the prospect's website (e.g. "ArchDaily").
        page_topic: Topic or title of the page where a link is sought.
        link_type: Strategy type — one of: guest_post | broken_link | resource | mention | directory.
        your_content_url: The alfaapanels.com URL to be featured/linked.
    """
    brand = SITE["brand"]
    domain = SITE["domain"]

    emails = {
        "broken_link": f"""Subject: Broken link on your {page_topic} page

Hi {prospect_name},

While reading your article on {page_topic} on {prospect_site}, I noticed a broken link that might be frustrating your visitors.

I have a well-maintained resource on aluminum composite panels at {your_content_url} that covers the same topic — it could be a great replacement.

Would you be open to swapping the broken link for this working resource?

Thanks for the great content!
[Your Name] | {brand} — {domain}""",

        "guest_post": f"""Subject: Guest article idea for {prospect_site}

Hi {prospect_name},

I've been following {prospect_site}'s coverage of {page_topic} — excellent work.

I'm a specialist in aluminum composite panels and facade cladding at {brand}. I'd like to contribute a guest article that adds real value for your audience — for example, "Specifying ACP Panels: What Architects Need to Know" or another topic that fits your editorial direction.

Would you be open to discussing a collaboration?

Best,
[Your Name] | {brand} — {domain}""",

        "resource": f"""Subject: Suggested addition to your {page_topic} page

Hi {prospect_name},

Your {page_topic} resource page on {prospect_site} is one of the most useful I've found in this space.

I wanted to suggest {your_content_url} from {brand} as a potential addition — it's a detailed, regularly updated guide on aluminum composite panels that I think your audience would find genuinely useful.

Happy to reciprocate with a mention on our site as well.

Best,
[Your Name] | {brand} — {domain}""",

        "mention": f"""Subject: Thank you for mentioning {brand}

Hi {prospect_name},

I came across your article on {page_topic} — thank you for mentioning {brand}!

Would you be open to adding a direct link to {your_content_url}? It would make it much easier for your readers to find the resource you referenced.

Really appreciate the support.
[Your Name] | {brand} — {domain}""",

        "directory": f"""Subject: {brand} listing for your {page_topic} directory

Hi {prospect_name},

I'd like to submit {brand} ({domain}) for inclusion in your {page_topic} directory.

{brand} manufactures and supplies high-quality aluminum composite panels and facade cladding systems used by architects, contractors, and builders on commercial and residential projects worldwide.

Please let me know if you need any additional information for the listing.

Best regards,
[Your Name] | {brand} — {domain}""",
    }
    return emails.get(link_type, emails["resource"])


@beta_tool
def track_opportunity(
    url: str,
    opportunity_type: str,
    priority: str,
    notes: str,
) -> str:
    """Record a newly discovered link-building opportunity.

    Args:
        url: URL of the prospect page or directory.
        opportunity_type: Category — guest_post | broken_link | resource | mention | directory | forum.
        priority: Urgency — HIGH | MEDIUM | LOW.
        notes: Summary of the opportunity and suggested next action.
    """
    return (
        f"TRACKED [{priority}] {opportunity_type}: {url}\n"
        f"Next step: {notes}"
    )


@beta_tool
def identify_link_gap(
    competitor_domain: str,
    linking_page_url: str,
    linking_page_topic: str,
) -> str:
    """Identify a competitor backlink as a link-gap opportunity for alfaapanels.com.

    Args:
        competitor_domain: The competitor that already has this backlink.
        linking_page_url: URL of the page that links to the competitor.
        linking_page_topic: Subject of the linking page.
    """
    return (
        f"LINK GAP FOUND\n"
        f"  Competitor with backlink: {competitor_domain}\n"
        f"  Linking page: {linking_page_url}\n"
        f"  Topic: {linking_page_topic}\n\n"
        f"Action plan:\n"
        f"  1. Visit {linking_page_url} and understand why they linked to {competitor_domain}\n"
        f"  2. Match or improve on the alfaapanels.com content that fits this context\n"
        f"  3. Send outreach within 48 hours offering alfaapanels.com as an additional/better resource\n"
        f"  4. Use generate_outreach_email(link_type='resource') to draft the email"
    )


# ── Agent runner ──────────────────────────────────────────────────────────────

def run_daily_agent(state: dict) -> tuple[str, list[dict]]:
    """Run today's backlink agent; return (report_text, new_opportunities)."""
    today = datetime.date.today()
    strategy = STRATEGY_BY_DAY[today.weekday()]
    task = STRATEGY_TASKS[strategy]

    # Avoid re-processing the same URLs
    seen_urls = {opp["url"] for opp in state.get("opportunities", [])}

    system = f"""You are an expert off-page SEO strategist building high-quality backlinks daily for {SITE['domain']} ({SITE['brand']}).

Site profile:
- Domain: {SITE['domain']}
- Brand: {SITE['brand']}
- Products: aluminum composite panels (ACP/ACM), facade cladding, exterior wall systems
- Target customers: architects, structural engineers, contractors, builders, fit-out companies
- Niche keywords: {', '.join(SITE['target_keywords'])}
- Competitors: {', '.join(SITE['competitors'])}
- Key pages: {', '.join(SITE['pages'].values())}

Today: {today} | Strategy: {strategy.replace('_', ' ').title()}

Already tracked URLs (skip these to avoid duplicates):
{chr(10).join(list(seen_urls)[:30]) if seen_urls else 'None yet — all fresh!'}

Rules:
1. Quality over quantity — only real, relevant prospects
2. Focus on construction, architecture, building materials, interior design niches
3. Outreach emails must be professional and personalised, never generic spam
4. Score every prospect with score_link_prospect() before including it
5. Track every found opportunity with track_opportunity()"""

    user_msg = f"""{task}

After completing the above:

## Daily Summary (required)
- Top 5 opportunities (URL, type, priority, outreach approach)
- 3 ready-to-send outreach emails (full text, copy-paste ready)
- 3 specific action items for today
- Any quick wins (free directory submissions, easy forum posts)"""

    client = anthropic.Anthropic()
    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        system=system,
        tools=[
            analyze_backlink_quality,
            score_link_prospect,
            generate_outreach_email,
            track_opportunity,
            identify_link_gap,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{"role": "user", "content": user_msg}],
    )

    report_parts: list[str] = []
    new_opportunities: list[dict] = []

    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_parts.append(block.text)
            elif block.type == "tool_use" and block.name == "track_opportunity":
                inp = block.input
                url = inp.get("url", "")
                if url and url not in seen_urls:
                    new_opportunities.append({
                        "url": url,
                        "type": inp.get("opportunity_type"),
                        "priority": inp.get("priority"),
                        "notes": inp.get("notes"),
                        "date": str(today),
                        "strategy": strategy,
                        "status": "new",
                    })
                    seen_urls.add(url)

    return "\n\n".join(report_parts), new_opportunities


# ── Report writer ─────────────────────────────────────────────────────────────

def save_report(report: str, state: dict, strategy: str) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    today = datetime.date.today()
    path = REPORTS_DIR / f"{today}_{strategy}.md"

    total = len(state.get("opportunities", []))
    high = sum(1 for o in state["opportunities"] if o.get("priority") == "HIGH")
    medium = sum(1 for o in state["opportunities"] if o.get("priority") == "MEDIUM")

    header = (
        f"# Daily Backlink Report — {SITE['brand']}\n\n"
        f"| Field | Value |\n"
        f"|---|---|\n"
        f"| Date | {today} |\n"
        f"| Domain | {SITE['domain']} |\n"
        f"| Strategy | {strategy.replace('_', ' ').title()} |\n"
        f"| Total opportunities tracked | {total} |\n"
        f"| High priority | {high} |\n"
        f"| Medium priority | {medium} |\n\n"
        f"---\n\n"
    )

    path.write_text(header + report, encoding="utf-8")
    return path


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    today = datetime.date.today()
    strategy = STRATEGY_BY_DAY[today.weekday()]

    print(f"\n{'='*60}")
    print(f"  Daily Backlink Builder — {SITE['domain']}")
    print(f"  Date     : {today}")
    print(f"  Strategy : {strategy.replace('_', ' ').title()}")
    print(f"{'='*60}\n")

    state = load_state()
    report, new_opps = run_daily_agent(state)

    state["opportunities"].extend(new_opps)
    state["runs"].append({
        "date": str(today),
        "strategy": strategy,
        "new_opportunities": len(new_opps),
    })
    save_state(state)

    report_path = save_report(report, state, strategy)

    print(f"\n{'='*60}")
    print(f"  New opportunities found : {len(new_opps)}")
    print(f"  Total tracked           : {len(state['opportunities'])}")
    print(f"  Report saved            : {report_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
