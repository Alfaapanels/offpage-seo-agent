"""
Daily Off-Page SEO & Backlink Builder for alfaapanels.com
Runs every day, rotates strategies, tracks prospects to avoid duplicates.
"""

import anthropic
import json
import os
import time
import schedule
from datetime import datetime, date
from pathlib import Path

# ── Site configuration ────────────────────────────────────────────────────────
SITE_CONFIG = {
    "domain": "alfaapanels.com",
    "brand_name": "Alfa Panels",
    "niche": "solar panels electrical panels energy solutions",
    "keywords": [
        "solar panels", "solar energy", "electrical panels",
        "solar installation", "renewable energy", "photovoltaic panels",
        "solar power system", "energy efficiency",
    ],
    "competitors": [
        "sunpowercorp.com",
        "lgsolarus.com",
        "canadiansolar.com",
        "jinko-solar.com",
    ],
}

# Day-of-week strategy rotation (0=Mon … 6=Sun)
DAILY_STRATEGY = {
    0: "brand_mentions",       # Monday  – find unlinked brand mentions
    1: "competitor_gaps",      # Tuesday – steal competitor backlinks
    2: "resource_pages",       # Wednesday – resource/link-roundup outreach
    3: "guest_post",           # Thursday – guest post pitches
    4: "broken_links",         # Friday  – broken-link replacement
    5: "forum_profiles",       # Saturday – community/forum profile links
    6: "directory_listings",   # Sunday  – niche directory submissions
}

TRACKER_FILE = Path("prospects_tracker.json")
REPORTS_DIR = Path("daily_reports")
REPORTS_DIR.mkdir(exist_ok=True)

client = anthropic.Anthropic()


# ── Tool implementations ──────────────────────────────────────────────────────

def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    signals = []
    generic = {"click here", "website", "here", "link", "read more", "visit"}
    if anchor_text.lower() in generic:
        signals.append("Warning: Generic anchor text – low SEO value")
    else:
        signals.append(f"Good: Descriptive anchor '{anchor_text}'")
    toxic = ["spam", "casino", "viagra", "porn", "adult", "malware"]
    if any(t in backlink_url.lower() for t in toxic):
        signals.append("TOXIC – disavow recommended")
    else:
        signals.append("Domain appears clean")
    authority = [".edu", ".gov", ".org"]
    if any(a in backlink_url for a in authority):
        signals.append("High-authority domain (.edu/.gov/.org)")
    return "\n".join(signals)


def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive = ["great", "best", "excellent", "recommend", "love", "amazing", "trusted", "quality"]
    negative = ["bad", "worst", "avoid", "scam", "terrible", "poor", "fake"]
    pos = sum(1 for w in positive if w in mention_text.lower())
    neg = sum(1 for w in negative if w in mention_text.lower())
    sentiment = "Positive" if pos > neg else "Negative" if neg > pos else "Neutral"
    kind = "Linked mention" if has_link else "Unlinked mention (link-building opportunity!)"
    action = "Monitor" if has_link else "Email site owner to add your link"
    return (
        f"Brand: {brand_name}\n"
        f"Type: {kind}\n"
        f"Sentiment: {sentiment}\n"
        f"Action: {action}"
    )


def score_link_prospect(page_url: str, page_title: str, snippet: str, niche: str) -> str:
    score = 0
    reasons = []
    niche_words = niche.lower().split()
    body = (page_title + " " + snippet).lower()
    relevance = sum(1 for w in niche_words if w in body)
    if relevance >= 3:
        score += 40
        reasons.append("High niche relevance (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate niche relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    resource_signals = ["resource", "guide", "tools", "blog", "list", "best", "top", "directory"]
    if any(s in page_url.lower() or s in page_title.lower() for s in resource_signals):
        score += 30
        reasons.append("Resource/guide/list page (+30)")
    authority = [".edu", ".gov", ".org"]
    if any(a in page_url for a in authority):
        score += 30
        reasons.append("High-authority domain (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return (
        f"Score: {score}/100 [{priority}]\n"
        f"URL: {page_url}\n"
        + "\n".join(reasons)
    )


def generate_outreach_email(
    prospect_name: str,
    prospect_site: str,
    page_topic: str,
    link_type: str,
    content_url: str,
) -> str:
    domain = SITE_CONFIG["domain"]
    brand = SITE_CONFIG["brand_name"]
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I was reading your article on {page_topic} at {prospect_site} and spotted a broken link.\n\n"
            f"I have an up-to-date resource on {page_topic} at {content_url} that would be a great replacement and adds real value for your readers.\n\n"
            f"Would you be open to updating it?\n\nBest regards,\n[Your Name]\n{brand} – {domain}"
        ),
        "guest_post": (
            f"Subject: Guest post idea for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I've been following {prospect_site}'s content on {page_topic} – great stuff!\n\n"
            f"I'd love to contribute a guest post. I run {brand} ({domain}), focusing on solar and electrical panels. "
            f"I can write something practical for your audience – for example:\n\n"
            f"  • 'How to Choose the Right Solar Panel System for Your Home'\n"
            f"  • 'Top 5 Mistakes in Solar Panel Installation'\n\n"
            f"Would you be open to a collaboration?\n\nBest,\n[Your Name]\n{brand} – {domain}"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {page_topic} at {prospect_site} is really comprehensive!\n\n"
            f"I thought your readers might also benefit from {content_url} – it covers {page_topic} from an installer's perspective with real-world data.\n\n"
            f"Would you consider adding it?\n\nThanks,\n[Your Name]\n{brand} – {domain}"
        ),
        "mention": (
            f"Subject: Thank you for mentioning {brand}!\n\n"
            f"Hi {prospect_name},\n\n"
            f"I noticed you mentioned {brand} in your article about {page_topic} – thank you!\n\n"
            f"Would you be open to linking directly to {content_url}? It would help your readers find us easily.\n\n"
            f"Happy to return the favour if helpful.\n\nWarm regards,\n[Your Name]\n{brand} – {domain}"
        ),
        "directory": (
            f"Subject: Listing submission – {brand}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I'd like to submit {brand} ({domain}) to your {page_topic} directory.\n\n"
            f"Category: Solar & Electrical Panels\n"
            f"Description: {brand} supplies and installs high-efficiency solar panels and electrical panels for residential and commercial properties.\n\n"
            f"Please let me know if you need anything else.\n\nBest,\n[Your Name]\n{brand} – {domain}"
        ),
    }
    return templates.get(link_type, templates["resource"])


def save_prospect(url: str, status: str, notes: str, outreach_email: str = "") -> str:
    tracker = _load_tracker()
    existing = next((p for p in tracker["prospects"] if p["url"] == url), None)
    if existing:
        existing.update({"status": status, "notes": notes, "updated": date.today().isoformat()})
        if outreach_email:
            existing["outreach_email"] = outreach_email
    else:
        tracker["prospects"].append({
            "url": url,
            "status": status,
            "notes": notes,
            "outreach_email": outreach_email,
            "added": date.today().isoformat(),
            "updated": date.today().isoformat(),
        })
    _save_tracker(tracker)
    return f"Saved prospect: {url} [{status}]"


def identify_link_gap(competitor: str, linking_page_topic: str) -> str:
    domain = SITE_CONFIG["domain"]
    return (
        f"LINK GAP OPPORTUNITY\n"
        f"Competitor with link: {competitor}\n"
        f"Your site: {domain}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Next steps:\n"
        f"1. Find what content earned {competitor} this link\n"
        f"2. Create a better / more up-to-date resource for {domain}\n"
        f"3. Pitch the linking site with your superior resource"
    )


# ── Tracker helpers ───────────────────────────────────────────────────────────

def _load_tracker() -> dict:
    if TRACKER_FILE.exists():
        with open(TRACKER_FILE) as f:
            return json.load(f)
    return {"prospects": [], "daily_summaries": {}}


def _save_tracker(data: dict) -> None:
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _already_contacted(url: str) -> bool:
    tracker = _load_tracker()
    return any(
        p["url"] == url and p["status"] in ("emailed", "backlink_live")
        for p in tracker["prospects"]
    )


# ── Tool registry ─────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "analyze_backlink_quality",
        "description": "Evaluate the quality and safety of a backlink pointing to alfaapanels.com.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url":          {"type": "string", "description": "Target URL (alfaapanels.com page)"},
                "backlink_url": {"type": "string", "description": "The URL that links to the target"},
                "anchor_text":  {"type": "string", "description": "Anchor text used in the link"},
            },
            "required": ["url", "backlink_url", "anchor_text"],
        },
    },
    {
        "name": "categorize_brand_mention",
        "description": "Detect whether a brand mention is linked or unlinked and its sentiment.",
        "input_schema": {
            "type": "object",
            "properties": {
                "mention_text": {"type": "string", "description": "Full text snippet containing the mention"},
                "brand_name":   {"type": "string", "description": "Brand name to look for"},
            },
            "required": ["mention_text", "brand_name"],
        },
    },
    {
        "name": "score_link_prospect",
        "description": "Score a potential link-building page and decide if it's worth pursuing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "page_url":   {"type": "string"},
                "page_title": {"type": "string"},
                "snippet":    {"type": "string", "description": "Short excerpt from the page"},
                "niche":      {"type": "string", "description": "Your site's niche"},
            },
            "required": ["page_url", "page_title", "snippet", "niche"],
        },
    },
    {
        "name": "generate_outreach_email",
        "description": "Write a personalised outreach email for a specific link-building tactic.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prospect_name": {"type": "string"},
                "prospect_site": {"type": "string"},
                "page_topic":    {"type": "string"},
                "link_type":     {
                    "type": "string",
                    "enum": ["broken_link", "guest_post", "resource", "mention", "directory"],
                },
                "content_url":   {"type": "string", "description": "alfaapanels.com page to link to"},
            },
            "required": ["prospect_name", "prospect_site", "page_topic", "link_type", "content_url"],
        },
    },
    {
        "name": "save_prospect",
        "description": "Persist a prospect to the tracking database so we don't contact them twice.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url":            {"type": "string"},
                "status":         {"type": "string", "enum": ["identified", "emailed", "backlink_live", "rejected"]},
                "notes":          {"type": "string"},
                "outreach_email": {"type": "string", "description": "Full email text (optional)"},
            },
            "required": ["url", "status", "notes"],
        },
    },
    {
        "name": "identify_link_gap",
        "description": "Describe a link-gap opportunity where a competitor has a backlink we don't.",
        "input_schema": {
            "type": "object",
            "properties": {
                "competitor":          {"type": "string", "description": "Competitor domain"},
                "linking_page_topic":  {"type": "string", "description": "Topic of the page linking to the competitor"},
            },
            "required": ["competitor", "linking_page_topic"],
        },
    },
    {"type": "web_search_20260209", "name": "web_search"},
    {"type": "web_fetch_20260209",  "name": "web_fetch"},
]


def _dispatch_tool(name: str, inp: dict) -> str:
    if name == "analyze_backlink_quality":
        return analyze_backlink_quality(**inp)
    if name == "categorize_brand_mention":
        return categorize_brand_mention(**inp)
    if name == "score_link_prospect":
        return score_link_prospect(**inp)
    if name == "generate_outreach_email":
        return generate_outreach_email(**inp)
    if name == "save_prospect":
        return save_prospect(**inp)
    if name == "identify_link_gap":
        return identify_link_gap(**inp)
    return f"Unknown tool: {name}"


# ── Agentic loop ──────────────────────────────────────────────────────────────

def run_agent(prompt: str, max_iters: int = 30) -> list[str]:
    messages = [{"role": "user", "content": prompt}]
    collected_text = []

    for iteration in range(max_iters):
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=16000,
            tools=TOOLS,
            messages=messages,
        )

        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(block.text)
                collected_text.append(block.text)

        if response.stop_reason == "end_turn":
            break

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  → [{block.name}]")
                    result = _dispatch_tool(block.name, block.input)
                    results.append({
                        "type":        "tool_result",
                        "tool_use_id": block.id,
                        "content":     str(result),
                    })
            messages.append({"role": "user", "content": results})
        else:
            break

    return collected_text


# ── Daily strategy prompts ────────────────────────────────────────────────────

def _build_prompt(strategy: str) -> str:
    cfg = SITE_CONFIG
    today = date.today().isoformat()
    tracker = _load_tracker()
    already_contacted = [p["url"] for p in tracker["prospects"] if p["status"] in ("emailed", "backlink_live")]
    skip_note = (
        f"\n\nALREADY CONTACTED (skip these): {', '.join(already_contacted[:20])}"
        if already_contacted else ""
    )

    base = (
        f"You are an expert off-page SEO specialist working for {cfg['brand_name']} ({cfg['domain']}).\n"
        f"Today is {today}. Domain: {cfg['domain']} | Niche: {cfg['niche']}\n"
        f"Keywords to target: {', '.join(cfg['keywords'][:5])}\n"
        f"Competitors: {', '.join(cfg['competitors'])}\n"
        f"{skip_note}\n\n"
        "IMPORTANT RULES:\n"
        "- Only pursue WHITE-HAT, genuine link-building tactics.\n"
        "- Save every real prospect using the save_prospect tool.\n"
        "- Generate ready-to-send outreach emails for the top 3 prospects.\n"
        "- End with a numbered action list for today.\n\n"
    )

    strategies = {
        "brand_mentions": (
            base +
            "TODAY'S TASK – BRAND MENTION AUDIT\n"
            f"1. Search: '\"Alfa Panels\" -site:{cfg['domain']}' and related brand variants.\n"
            "2. For each mention found, use categorize_brand_mention to classify it.\n"
            "3. For unlinked mentions with positive/neutral sentiment, generate a 'mention' outreach email.\n"
            "4. Score and save the top 5 prospects.\n"
            "5. Summarise: how many unlinked mentions found, estimated link value."
        ),
        "competitor_gaps": (
            base +
            "TODAY'S TASK – COMPETITOR BACKLINK GAP ANALYSIS\n"
            f"1. For each competitor in {cfg['competitors']}, search: 'link:{competitor} solar panels'.\n"
            "2. Find sites linking to competitors but likely NOT to alfaapanels.com.\n"
            "3. Use identify_link_gap for each opportunity.\n"
            "4. Score the top prospects with score_link_prospect.\n"
            "5. Generate a 'resource' outreach email for the top 3.\n"
            "6. Save all identified prospects."
        ).replace("{competitor}", cfg['competitors'][0]),
        "resource_pages": (
            base +
            "TODAY'S TASK – RESOURCE PAGE LINK BUILDING\n"
            "1. Search for resource/link pages in the solar & energy niche:\n"
            "   - 'solar energy resources inurl:resources'\n"
            "   - 'renewable energy links \"solar panels\"'\n"
            "   - 'electrical panels guide intitle:resources'\n"
            "2. For each, fetch the page and check if alfaapanels.com is listed.\n"
            "3. Score each with score_link_prospect.\n"
            "4. Generate a 'resource' outreach email for the top 3 (score >= 40).\n"
            "5. Save prospects with status 'identified'."
        ),
        "guest_post": (
            base +
            "TODAY'S TASK – GUEST POST OUTREACH\n"
            "1. Search for blogs accepting guest posts:\n"
            "   - 'solar energy blog \"write for us\"'\n"
            "   - 'renewable energy \"guest post\" OR \"guest article\"'\n"
            "   - 'electrical installation blog \"contribute\"'\n"
            "2. Fetch each candidate to confirm it's real and active.\n"
            "3. Score with score_link_prospect.\n"
            "4. Generate a 'guest_post' outreach email for the top 3.\n"
            "5. Save all prospects."
        ),
        "broken_links": (
            base +
            "TODAY'S TASK – BROKEN LINK REPLACEMENT\n"
            "1. Search for resource/guide pages in the solar/energy niche.\n"
            "2. Fetch pages and look for 404 / dead external links.\n"
            "3. For each broken link, identify what alfaapanels.com content could replace it.\n"
            "4. Use analyze_backlink_quality on the prospective link.\n"
            "5. Generate a 'broken_link' outreach email for the top 3 opportunities.\n"
            "6. Save all prospects."
        ),
        "forum_profiles": (
            base +
            "TODAY'S TASK – FORUM & COMMUNITY PROFILE LINKS\n"
            "1. Search for active solar/energy/construction forums and Q&A communities:\n"
            "   - Reddit communities (r/solar, r/DIYsolar, r/homeimprovement)\n"
            "   - Quora topics on solar panels\n"
            "   - Niche forums about renewable energy\n"
            "2. For each community found, assess if a profile link or helpful answer linking to alfaapanels.com would be appropriate.\n"
            "3. Draft 3 genuinely helpful community answers/posts that naturally mention alfaapanels.com.\n"
            "4. Save prospects with notes on which community and what to post."
        ),
        "directory_listings": (
            base +
            "TODAY'S TASK – NICHE DIRECTORY SUBMISSIONS\n"
            "1. Search for niche directories:\n"
            "   - 'solar panel company directory'\n"
            "   - 'renewable energy business directory'\n"
            "   - 'electrical contractor directory'\n"
            "   - 'green business directory list'\n"
            "2. Fetch each to confirm it's a real, active directory (not spam).\n"
            "3. Score with score_link_prospect.\n"
            "4. Generate a 'directory' outreach email for the top 5.\n"
            "5. Save prospects."
        ),
    }
    return strategies.get(strategy, strategies["resource_pages"])


# ── Daily runner ──────────────────────────────────────────────────────────────

def run_daily_backlink_session():
    today = date.today()
    strategy = DAILY_STRATEGY[today.weekday()]

    print(f"\n{'='*65}")
    print(f"  Daily Backlink Builder – {today.isoformat()}")
    print(f"  Site   : {SITE_CONFIG['domain']}")
    print(f"  Strategy: {strategy.replace('_', ' ').title()}")
    print(f"{'='*65}\n")

    prompt = _build_prompt(strategy)
    report_text = run_agent(prompt)

    # Save daily report
    report_path = REPORTS_DIR / f"{today.isoformat()}_{strategy}.md"
    with open(report_path, "w") as f:
        f.write(f"# Backlink Report – {today.isoformat()}\n")
        f.write(f"**Site:** {SITE_CONFIG['domain']}  \n")
        f.write(f"**Strategy:** {strategy.replace('_', ' ').title()}  \n\n")
        f.write("---\n\n")
        f.write("\n\n".join(report_text))

    # Update summary in tracker
    tracker = _load_tracker()
    tracker["daily_summaries"][today.isoformat()] = {
        "strategy": strategy,
        "report_file": str(report_path),
        "prospects_before": len(tracker["prospects"]),
    }
    _save_tracker(tracker)

    print(f"\n Report saved → {report_path}")
    print(f" Prospects tracked: {len(tracker['prospects'])}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    print("Starting Daily Backlink Builder for alfaapanels.com")

    # Run immediately on startup
    run_daily_backlink_session()

    # Schedule future daily runs at 09:00
    schedule.every().day.at("09:00").do(run_daily_backlink_session)

    print("\nAgent scheduled – runs every day at 09:00.")
    print("Press Ctrl+C to stop.\n")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
